from __future__ import annotations

import math
import struct
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Part:
    ref: str
    kind: str
    x: int
    y: int
    min_gap: int


def marker(ref: str) -> bytes:
    raw = ref.encode("ascii")
    return b"\xff" + bytes([len(raw)]) + raw


def i32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<i", data, offset)[0]


def component_ranges(data: bytes, max_index: int = 64) -> dict[str, tuple[int, int]]:
    refs = ["LCD1", "X1"]
    refs += [f"U{i}" for i in range(1, max_index + 1)]
    refs += [f"R{i}" for i in range(1, max_index + 1)]
    refs += [f"C{i}" for i in range(1, max_index + 1)]
    marks: list[tuple[int, str]] = []
    for ref in refs:
        pos = data.find(marker(ref))
        if pos >= 0:
            marks.append((pos, ref))
    marks.sort()
    return {
        ref: (start, marks[index + 1][0] if index + 1 < len(marks) else len(data))
        for index, (start, ref) in enumerate(marks)
    }


def direct_origin(data: bytes, ref: str, start: int) -> tuple[int, int] | None:
    if ref == "LCD1":
        return None
    offset = start + 2 + len(ref)
    if offset + 8 > len(data):
        return None
    x, y = i32(data, offset), i32(data, offset + 4)
    if -30_000_000 <= x <= 30_000_000 and -30_000_000 <= y <= 30_000_000:
        return x, y
    return None


def lcd_origin_guess(data: bytes, start: int, end: int) -> tuple[int, int] | None:
    candidates: dict[tuple[int, int], int] = {}
    for offset in range(start, max(start, end - 7)):
        x, y = i32(data, offset), i32(data, offset + 4)
        if -15_000_000 <= x <= 15_000_000 and -10_000_000 <= y <= 10_000_000:
            if abs(x) > 500_000 or abs(y) > 500_000:
                candidates[(x, y)] = candidates.get((x, y), 0) + 1
    if not candidates:
        return None
    return max(candidates.items(), key=lambda item: item[1])[0]


def kind_for(record: bytes) -> str:
    if b"AT89C52" in record or b"AT89C51" in record:
        return "MCU"
    if b"DS18B20" in record:
        return "DS18B20"
    if b"LM016L" in record or b"LCD" in record:
        return "LCD"
    if b"RES" in record:
        return "RES"
    if b"CAP" in record:
        return "CAP"
    if b"XTAL" in record or b"CRYSTAL" in record:
        return "XTAL"
    return "OTHER"


def min_gap_for(kind: str) -> int:
    return {
        "MCU": 2_400_000,
        "LCD": 3_000_000,
        "DS18B20": 1_600_000,
        "RES": 900_000,
        "CAP": 650_000,
        "XTAL": 850_000,
    }.get(kind, 700_000)


def audit_project(project: str | Path, required_refs: list[str] | None = None) -> dict[str, Any]:
    project_path = Path(project)
    with zipfile.ZipFile(project_path, "r") as zf:
        data = zf.read("ROOT.DSN")

    ranges = component_ranges(data)
    parts: list[Part] = []
    warnings: list[str] = []
    for ref, (start, end) in sorted(ranges.items(), key=lambda item: item[1][0]):
        record = data[start:end]
        kind = kind_for(record)
        origin = lcd_origin_guess(data, start, end) if ref == "LCD1" else direct_origin(data, ref, start)
        if origin is None:
            warnings.append(f"missing-origin {ref} kind={kind} range={start}:{end}")
            continue
        parts.append(Part(ref=ref, kind=kind, x=origin[0], y=origin[1], min_gap=min_gap_for(kind)))

    issues: list[dict[str, Any]] = []
    for index, left in enumerate(parts):
        for right in parts[index + 1 :]:
            distance = math.hypot(left.x - right.x, left.y - right.y)
            threshold = max(left.min_gap, right.min_gap)
            if distance < threshold:
                issues.append(
                    {
                        "type": "too_close",
                        "a": left.ref,
                        "b": right.ref,
                        "distance": round(distance),
                        "threshold": threshold,
                    }
                )

    if required_refs:
        found = {part.ref for part in parts}
        for ref in required_refs:
            if ref not in found:
                issues.append({"type": "missing_ref", "ref": ref})

    return {
        "ok": not issues,
        "project": str(project_path),
        "part_count": len(parts),
        "parts": [asdict(part) for part in parts],
        "issues": issues,
        "warnings": warnings,
    }
