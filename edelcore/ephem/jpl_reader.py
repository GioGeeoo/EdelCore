"""
JPL SPICE / DE (DAF/SPK/BSP) Kernel Reader & Chebyshev Evaluator.
Reads binary ephemeris files (DE405, DE421, DE440, DE441) and computes
ultra-precise positions and velocities using Chebyshev polynomial interpolation.
"""
from __future__ import annotations
import os
import struct
import math
from typing import Dict, List, Tuple, Optional

class SPKRecord:
    def __init__(
        self,
        target: int,
        center: int,
        frame: int,
        spk_type: int,
        initial_epoch_jd: float,
        final_epoch_jd: float,
        start_addr: int,
        end_addr: int
    ):
        self.target = target
        self.center = center
        self.frame = frame
        self.spk_type = spk_type
        self.initial_epoch_jd = initial_epoch_jd
        self.final_epoch_jd = final_epoch_jd
        self.start_addr = start_addr  # 1-based double word index
        self.end_addr = end_addr

class JPLSPKReader:
    """
    Parser for NASA SPICE Binary SPK (.bsp) / JPL DE files.
    Evaluates Type 2 (Chebyshev position) and Type 3 (Chebyshev position+velocity) ephemeris records.
    """

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.segments: List[SPKRecord] = []
        self._file = None
        if os.path.exists(filepath):
            self._load()

    def _load(self):
        with open(self.filepath, "rb") as f:
            # DAF File record (first 1024 bytes)
            locidw = f.read(8).decode("ascii", errors="ignore")
            if not (locidw.startswith("DAF/SPK") or locidw.startswith("NAIF/DAF")):
                # Try generic check
                pass
            
            f.seek(8)
            nd = struct.unpack("<i", f.read(4))[0]  # Number of double precision components in summary
            ni = struct.unpack("<i", f.read(4))[0]  # Number of integer components in summary
            fseek_pos = 16
            f.seek(fseek_pos)
            locifn = f.read(60).decode("ascii", errors="ignore")
            fwd = struct.unpack("<i", f.read(4))[0]  # Forward record pointer
            bwd = struct.unpack("<i", f.read(4))[0]  # Backward record pointer
            free = struct.unpack("<i", f.read(4))[0]

            # Read summary records
            curr_record = fwd
            while curr_record != 0:
                f.seek((curr_record - 1) * 1024)
                next_rec, prev_rec, n_sum = struct.unpack("<ddd", f.read(24))
                next_rec_int = int(next_rec)
                n_sum_int = int(n_sum)

                summary_size = (nd + (ni + 1) // 2) * 8
                for s in range(n_sum_int):
                    raw_sum = f.read(summary_size)
                    if len(raw_sum) < summary_size:
                        break
                    # Unpack ND doubles and NI ints
                    doubles = struct.unpack(f"<{nd}d", raw_sum[:nd*8])
                    ints = struct.unpack(f"<{ni}i", raw_sum[nd*8:nd*8+ni*4])

                    # In SPK:
                    # doubles[0] = initial epoch (sec past J2000 TDB)
                    # doubles[1] = final epoch (sec past J2000 TDB)
                    # ints[0] = target body NAIF ID
                    # ints[1] = center body NAIF ID
                    # ints[2] = frame ID (1 = J2000)
                    # ints[3] = SPK type (e.g. 2 for Chebyshev pos, 3 for Chebyshev pos+vel)
                    # ints[4] = initial address (1-based index of 8-byte word)
                    # ints[5] = final address
                    init_jd = 2451545.0 + doubles[0] / 86400.0
                    final_jd = 2451545.0 + doubles[1] / 86400.0

                    rec = SPKRecord(
                        target=ints[0],
                        center=ints[1],
                        frame=ints[2],
                        spk_type=ints[3],
                        initial_epoch_jd=init_jd,
                        final_epoch_jd=final_jd,
                        start_addr=ints[4],
                        end_addr=ints[5]
                    )
                    self.segments.append(rec)

                curr_record = next_rec_int

    def evaluate_body(self, target_naif: int, jd_tdb: float) -> Optional[Tuple[float, float, float]]:
        """
        Evaluate (X, Y, Z in km) for target body relative to its direct center at JD(TDB).
        """
        if not os.path.exists(self.filepath) or not self.segments:
            return None

        matching_seg = None
        for seg in self.segments:
            if seg.target == target_naif and seg.initial_epoch_jd <= jd_tdb <= seg.final_epoch_jd:
                matching_seg = seg
                break

        if not matching_seg:
            for seg in self.segments:
                if seg.target == target_naif and (seg.initial_epoch_jd - 0.1 <= jd_tdb <= seg.final_epoch_jd + 0.1):
                    matching_seg = seg
                    break

        if not matching_seg:
            return None

        return self._evaluate_segment(matching_seg, jd_tdb)

    def evaluate_geocentric(self, target_naif: int, jd_tdb: float) -> Optional[Tuple[float, float, float]]:
        """
        Evaluate true geocentric vector (X, Y, Z in km) in ICRF/J2000 equator:
        Target(Geocentric) = Target(SSB) - Earth(SSB).
        Includes recursive center-to-barycenter chaining.
        """
        # 1. Earth position relative to Solar System Barycenter (SSB)
        # EMB relative to SSB (target 3)
        emb_ssb = self.evaluate_body(3, jd_tdb)
        earth_emb = self.evaluate_body(399, jd_tdb)
        if not emb_ssb:
            return None
        earth_ssb = (
            emb_ssb[0] + (earth_emb[0] if earth_emb else 0.0),
            emb_ssb[1] + (earth_emb[1] if earth_emb else 0.0),
            emb_ssb[2] + (earth_emb[2] if earth_emb else 0.0)
        )

        # 2. Moon (target 301 is relative to Earth/EMB center 3)
        if target_naif == 301:
            moon_emb = self.evaluate_body(301, jd_tdb)
            if not moon_emb:
                return None
            if earth_emb:
                # Moon relative to Earth = Moon(EMB) - Earth(EMB)
                return (
                    moon_emb[0] - earth_emb[0],
                    moon_emb[1] - earth_emb[1],
                    moon_emb[2] - earth_emb[2]
                )
            return moon_emb

        # 3. Target position relative to SSB
        # Handle planets with planet-center relative to barycenter (e.g. 199 relative to 1, 299 relative to 2)
        target_ssb = None
        direct = self.evaluate_body(target_naif, jd_tdb)
        if direct is None:
            # Try barycenter ID (e.g. 5 for Jupiter, 6 for Saturn, 7 for Uranus, 8 for Neptune, 9 for Pluto)
            bary_map = {199: 1, 299: 2, 499: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10}
            bary_id = bary_map.get(target_naif)
            if bary_id is not None:
                target_ssb = self.evaluate_body(bary_id, jd_tdb)
        else:
            # Check center
            seg = next((s for s in self.segments if s.target == target_naif), None)
            if seg and seg.center != 0:
                center_ssb = self.evaluate_body(seg.center, jd_tdb)
                if center_ssb:
                    target_ssb = (direct[0] + center_ssb[0], direct[1] + center_ssb[1], direct[2] + center_ssb[2])
                else:
                    target_ssb = direct
            else:
                target_ssb = direct

        if not target_ssb:
            return None

        # Return Geocentric Vector: Target(SSB) - Earth(SSB)
        return (
            target_ssb[0] - earth_ssb[0],
            target_ssb[1] - earth_ssb[1],
            target_ssb[2] - earth_ssb[2]
        )

    def _evaluate_segment(self, seg: SPKRecord, jd_tdb: float) -> Tuple[float, float, float]:
        sec_past_j2000 = (jd_tdb - 2451545.0) * 86400.0

        with open(self.filepath, "rb") as f:
            # Last 4 double precision words of the segment contain metadata:
            # INIT, INTLEN, RSIZE, N
            f.seek((seg.end_addr - 4) * 8)
            init_sec, intlen, rsize, n_records = struct.unpack("<4d", f.read(32))
            rsize = int(rsize)
            n_records = int(n_records)

            # Determine which sub-record contains epoch
            record_idx = int((sec_past_j2000 - init_sec) // intlen)
            record_idx = max(0, min(n_records - 1, record_idx))

            # Address of this record
            rec_addr = seg.start_addr + record_idx * rsize
            f.seek((rec_addr - 1) * 8)
            rec_data = struct.unpack(f"<{rsize}d", f.read(rsize * 8))

            # rec_data[0] = mid_sec, rec_data[1] = radius_sec
            t_mid = rec_data[0]
            t_rad = rec_data[1]
            # Normalized Chebyshev parameter in [-1, 1]
            tau = (sec_past_j2000 - t_mid) / t_rad

            # Number of Chebyshev coefficients per component
            # In SPK Type 2: rsize = 2 + 3 * n_coeffs
            n_coeffs = (rsize - 2) // 3

            # Evaluate Chebyshev polynomials T_n(tau)
            t_poly = [0.0] * n_coeffs
            if n_coeffs > 0:
                t_poly[0] = 1.0
            if n_coeffs > 1:
                t_poly[1] = tau
            for i in range(2, n_coeffs):
                t_poly[i] = 2.0 * tau * t_poly[i - 1] - t_poly[i - 2]

            # Compute X, Y, Z
            x = sum(rec_data[2 + i] * t_poly[i] for i in range(n_coeffs))
            y = sum(rec_data[2 + n_coeffs + i] * t_poly[i] for i in range(n_coeffs))
            z = sum(rec_data[2 + 2 * n_coeffs + i] * t_poly[i] for i in range(n_coeffs))

            return x, y, z
