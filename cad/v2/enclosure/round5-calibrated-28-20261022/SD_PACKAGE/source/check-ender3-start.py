#!/usr/bin/env python3

import sys
import re
from pathlib import Path

def fail(message):
    print()
    print("ENDER 3 SAFETY CHECK FAILED")
    print(message)
    print("REFUSING GENERATED G-CODE")
    sys.exit(99)

if len(sys.argv) < 2:
    fail("OrcaSlicer did not provide a G-code filename.")

gcode_path = Path(sys.argv[-1])

if not gcode_path.is_file():
    fail(f"G-code file does not exist: {gcode_path}")

with gcode_path.open("r", encoding="utf-8", errors="ignore") as f:
    lines = [next(f, "") for _ in range(1500)]

text = "".join(lines)

required = [
    ("safety marker", r"(?m)^\s*;\s*JIM_ENDER3_SAFE_START_V1\s*$"),
    ("G28 homing", r"(?m)^\s*G28(?:\s*;.*)?$"),
    ("saved mesh enable", r"(?m)^\s*M420\s+S1(?:\s|;|$)"),
    ("left purge start", r"(?m)^\s*G1\s+X10(?:\.0+)?\s+Y20(?:\.0+)?\s+F3600(?:\s|;|$)"),
    ("first left purge line", r"(?m)^\s*G1\s+Y180(?:\.0+)?\s+E5\.6(?:0+)?\s+F900(?:\s|;|$)"),
    ("purge-line shift", r"(?m)^\s*G1\s+X10\.5(?:0+)?\s+F1800(?:\s|;|$)"),
    ("second left purge line", r"(?m)^\s*G1\s+Y20(?:\.0+)?\s+E5\.6(?:0+)?\s+F900(?:\s|;|$)"),
]

positions = []

for name, pattern in required:
    match = re.search(pattern, text)
    if not match:
        fail(f"Missing required command: {name}")
    positions.append(match.start())

if positions != sorted(positions):
    fail("Required start-G-code commands are not in the expected order.")

bad_patterns = [
    r"(?m)^\s*G1\s+X205(?:\.0+)?\s+E19(?:\.0+)?\s+F1000",
    r"(?m)^\s*G1\s+Y1(?:\.0+)?\s+Z0\.3(?:0+)?\s+F1000",
]

for pattern in bad_patterns:
    if re.search(pattern, text):
        fail("Detected the bad front-edge purge routine.")

print("ENDER 3 SAFETY CHECK PASSED")
sys.exit(0)
