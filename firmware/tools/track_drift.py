#!/usr/bin/env python3
"""Measure straight-line track drift through the C6 field API (Gladiator-Gateway, 192.168.8.1).

Each run sends slightly UNEQUAL left/right commands, which the S3 never trims (its straight
trim only rewrites exactly equal pairs), so every run measures the raw tracks. The IMU game
yaw rate over the settled part of the run is the drift. Fitting drift against the trim and
finding where it crosses zero gives the trim that drives straight.

  T  signed trim percent, same meaning as src/drive/StraightTrim.h:
     T > 0 holds the LEFT track back, T < 0 holds the RIGHT track back.
     strong = p*(100+|T|)/100 (max 100), weak = strong*(100-|T|)/(100+|T|).
     The installed firmware (Orientation.h) boosts LEFT by 14% forward / 22% reverse,
     which is T = -14 forward and T = -22 reverse at 50% power.

Without --go: preflight only, nothing moves.
With --go: each run arms, drives for RUN_S with the dead-man held, stops, and disarms.
Any error, Ctrl+C, IMU loss, stale data or a turn over RUNAWAY_DEG stops and disarms.
The S3 also coasts on its own if commands stop for 350 ms.
"""
import argparse
import json
import random
import statistics
import sys
import threading
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HOST = "http://192.168.8.1"
SEND_S = 0.10
RUN_S = 2.0              # 2.8 s at 50% ran Jim's robot into a cabinet on 2026-11-09
SETTLE_S = 0.6
REST_S = 3.0
RUNAWAY_DEG = 45.0
MIN_RATE_SAMPLES = 6     # a run cut short by an IMU dropout still counts if this many settled samples exist
MIN_VOLTS = 13.5
OUT = Path(__file__).resolve().parent.parent / "diagnostics" / "track-drift-20261109"


def get(path, timeout=0.6):
    with urllib.request.urlopen(HOST + path, timeout=timeout) as r:
        return json.load(r)


def post(path, body, timeout=1.0):
    req = urllib.request.Request(HOST + path, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode() or "{}")


class Field:
    """Polls /api/field in the background; keeps the latest snapshot and an IMU log."""

    def __init__(self):
        self.lock = threading.Lock()
        self.snap = None
        self.at = 0.0
        self.log = None
        self.errors = 0
        self.stop = False
        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        while not self.stop:
            try:
                s = get("/api/field")
                now = time.monotonic()
                with self.lock:
                    self.snap, self.at = s, now
                    if self.log is not None:
                        imu = s["sensors"]["imu"]
                        c = s["controller"]
                        self.log.append({"t": now, "imuMs": imu["s3Ms"], "valid": imu["gameDerived"]["valid"],
                                         "yaw": imu["gameDerived"]["yawDeg"], "left": c["leftPercent"],
                                         "right": c["rightPercent"], "armed": c["armed"], "volts": s.get("volts")})
            except Exception:
                with self.lock:
                    self.errors += 1
            time.sleep(0.05)

    def latest(self):
        with self.lock:
            return self.snap, self.at

    def s3_now(self):
        s, at = self.latest()
        return int(s["controller"]["s3Ms"] + (time.monotonic() - at) * 1000)


def tracks(direction, trim, power):
    a = min(abs(trim), 60)
    strong = min(100, round(power * (100 + a) / 100))
    weak = round(strong * (100 - a) / (100 + a))
    if strong == weak:
        weak = strong - 1  # equal pairs would get the firmware trim
    left, right = (weak, strong) if trim >= 0 else (strong, weak)
    return (left, right) if direction == "forward" else (-left, -right)


def preflight(field, quiet=False):
    s, at = field.latest()
    problems = []
    if s is None or time.monotonic() - at > 0.5:
        return ["no fresh /api/field data"]
    c = s["controller"]
    imu = s["sensors"]["imu"]
    if not s.get("connected"): problems.append("S3 not connected")
    if c.get("armed"): problems.append(f"another controller is armed (client {c.get('client')})")
    if c.get("batteryLockout"): problems.append("battery lockout")
    if c.get("state") not in ("SAFE", "ARMED", "DRIVE"): problems.append(f"state {c.get('state')}")
    if not s.get("powerValid") or (s.get("volts") or 0) < MIN_VOLTS: problems.append(f"battery {s.get('volts')} V")
    if not imu["gameDerived"]["valid"] or imu["meta"]["health"] != "OK": problems.append("IMU game yaw not valid")
    if (s.get("telemetryAgeMs") or 9999) > 300: problems.append("S3 telemetry stale")
    if c.get("leftPercent") or c.get("rightPercent"): problems.append("tracks not at zero")
    if not quiet:
        print(f"  S3 {c.get('state')}, armed {c.get('armed')}, battery {s.get('volts'):.2f} V, "
              f"IMU {imu['meta']['health']} game yaw {imu['gameDerived']['yawDeg']:.1f}")
    return problems


class Driver:
    def __init__(self, field):
        self.field = field
        self.client = random.randint(1, 2**32 - 1)
        self.seq = 0
        self.epoch = None

    def send(self, op, left=0, right=0, deadman=0):
        s, _ = self.field.latest()
        if self.epoch is None or op == 1:
            self.epoch = s["controller"]["epoch"]
        self.seq += 1
        body = {"epoch": self.epoch, "client": self.client, "sequence": self.seq,
                "observedMs": self.field.s3_now(), "operation": op, "deadman": deadman, "overdrive": 0,
                "power": max(abs(left), abs(right), 1) if op == 2 else 25, "left": left, "right": right}
        r = post("/api/control", body)
        if "epoch" in r:
            self.epoch = r["epoch"]
        return r.get("result", 0)

    def safe_stop(self):
        for op in (2, 0, 0):
            try:
                self.send(op)
            except Exception:
                pass
            time.sleep(0.05)
        self.epoch = None


def yaw_rate(rows, start, end):
    pts = [r for r in rows if start <= r["t"] <= end and r["valid"]]
    if len(pts) < MIN_RATE_SAMPLES:
        raise RuntimeError(f"only {len(pts)} IMU samples in the settled window")
    ts, ys, prev, off = [], [], None, 0.0
    t0 = pts[0]["imuMs"]
    for r in pts:
        y = r["yaw"]
        if prev is not None:
            d = y - prev
            if d > 180: off -= 360
            elif d < -180: off += 360
        prev = y
        ts.append((r["imuMs"] - t0) / 1000.0)
        ys.append(y + off)
    mt, my = statistics.fmean(ts), statistics.fmean(ys)
    sxx = sum((t - mt) ** 2 for t in ts)
    slope = sum((t - mt) * (y - my) for t, y in zip(ts, ys)) / sxx
    return slope, len(pts), ys[-1] - ys[0]


def run_once(field, drv, direction, trim, power):
    left, right = tracks(direction, trim, power)
    problems = preflight(field, quiet=True)
    if problems:
        raise RuntimeError("preflight: " + "; ".join(problems))
    with field.lock:
        field.log = []
    if drv.send(1) != 0:
        raise RuntimeError("arm rejected")
    time.sleep(0.15)
    t_start = time.monotonic()
    yaw0 = field.latest()[0]["sensors"]["imu"]["gameDerived"]["yawDeg"]
    stopped = None
    try:
        while time.monotonic() - t_start < RUN_S:
            try:
                res = drv.send(2, left, right, 1)
            except Exception as e:  # slow C6 reply: stop this run, keep its data
                stopped = f"control request failed ({e})"
                break
            if res != 0:
                stopped = f"S3 rejected drive command (result {res})"
                break
            s, at = field.latest()
            if time.monotonic() - at > 0.4:
                raise RuntimeError("field data went stale")
            imu = s["sensors"]["imu"]["gameDerived"]
            if not imu["valid"]:
                stopped = "IMU game yaw went invalid"
                break
            turned = (imu["yawDeg"] - yaw0 + 180) % 360 - 180
            if abs(turned) > RUNAWAY_DEG:
                stopped = f"turned {turned:.0f} deg"
                break
            time.sleep(SEND_S)
        t_end = time.monotonic()
    finally:
        drv.safe_stop()
        with field.lock:
            rows = list(field.log or [])
        (OUT / f"last-run-{direction}-{trim:+.0f}-raw.json").write_text(json.dumps(rows))
    time.sleep(0.3)
    with field.lock:
        rows, field.log = field.log, None
    if stopped:
        print(f"  run cut short: {stopped} after {t_end - t_start:.1f} s")
    rate, n, total = yaw_rate(rows, t_start + SETTLE_S, t_end)
    seen = [(r["left"], r["right"]) for r in rows if t_start + SETTLE_S <= r["t"] <= t_end]
    applied = max(set(seen), key=seen.count) if seen else None
    return {"direction": direction, "trim": trim, "power": power, "left": left, "right": right,
            "appliedLeftRight": applied, "cutShort": stopped, "runS": round(t_end - t_start, 2), "yawRateDegPerS": round(rate, 2), "samples": n,
            "settledTurnDeg": round(total, 1), "volts": rows[-1]["volts"] if rows else None, "rows": rows}


def fit(rows):
    xs = [r["trim"] for r in rows]
    ys = [r["yawRateDegPerS"] for r in rows]
    if len(set(xs)) < 2:
        return None
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    icpt = my - slope * mx
    return {"slope": round(slope, 3), "intercept": round(icpt, 2),
            "zeroTrim": round(-icpt / slope, 1) if slope else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--power", type=int, default=50)
    ap.add_argument("--forward", type=float, nargs="*", default=[-14, -7, 0])
    ap.add_argument("--reverse", type=float, nargs="*", default=[-22, -11, 0])
    ap.add_argument("--label", default="stage1")
    ap.add_argument("--go", action="store_true")
    a = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    field = Field()
    time.sleep(0.6)
    print("Preflight:")
    problems = preflight(field)
    plan = []
    for i in range(max(len(a.forward), len(a.reverse))):
        if i < len(a.forward): plan.append(("forward", a.forward[i]))
        if i < len(a.reverse): plan.append(("reverse", a.reverse[i]))
    print(f"Plan at {a.power}% power, {RUN_S}s per run, alternating forward/back:")
    for d, t in plan:
        print(f"  {d:8s} T={t:+5.1f}  left/right = {tracks(d, t, a.power)}")
    if problems:
        print("NOT READY: " + "; ".join(problems))
        return 2
    if not a.go:
        print("Preflight OK. Nothing moved (no --go).")
        return 0

    drv = Driver(field)
    results = []
    try:
        for d, t in plan:
            r = run_once(field, drv, d, t, a.power)
            results.append(r)
            print(f"  {d:8s} T={t:+5.1f} cmd {r['left']:+d}/{r['right']:+d} applied {r['appliedLeftRight']} "
                  f"-> {r['yawRateDegPerS']:+6.2f} deg/s ({r['settledTurnDeg']:+.1f} deg, {r['samples']} samples)")
            time.sleep(REST_S)
    except KeyboardInterrupt:
        print("Stopped by Ctrl+C.")
    except Exception as e:
        print(f"ABORTED: {e}")
    finally:
        drv.safe_stop()
        field.stop = True
    summary = {"atUtc": datetime.now(timezone.utc).isoformat(), "label": a.label, "power": a.power,
               "runS": RUN_S, "settleS": SETTLE_S,
               "fit": {d: fit([r for r in results if r["direction"] == d]) for d in ("forward", "reverse")},
               "runs": [{k: v for k, v in r.items() if k != "rows"} for r in results]}
    stamp = datetime.now().strftime("%H%M%S")
    (OUT / f"{a.label}-{stamp}.json").write_text(json.dumps(summary, indent=2))
    (OUT / f"{a.label}-{stamp}-raw.json").write_text(json.dumps([r["rows"] for r in results]))
    for d, f in summary["fit"].items():
        if f: print(f"{d}: rate = {f['slope']}*T + {f['intercept']} deg/s, straight at T = {f['zeroTrim']}")
    print(f"Saved {OUT / (a.label + '-' + stamp + '.json')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
