#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
nutzraum.py — ROM.os · Nutzraum Continuum 729 + Kartor v2
Records-API (raw_os_last, kartor_registry), Continuum (729),
Kartor-Coverage/Balance, Pipeline rueckwaerts = roh machen.
  python3 nutzraum.py --serve       # http://127.0.0.1:8787/rom.html
  python3 nutzraum.py --print       # alle 729 Slots
  python3 nutzraum.py --best 40     # raueste Optionen fuer Zelle 40
  python3 nutzraum.py --pipeline    # Rueckwaerts-Suite Demo
  python3 nutzraum.py --kartor      # Coverage + Balance je Ebene
"""
import json, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
TRITS  = ["ROH", "BEARBEITET", "FREI"]
SCORES = [4, 3.5, 3, 3, 2, 1.5, 1, 0.5, 0]
CELLS  = 81
LEVELS = [3, 9, 27, 81, 243, 729]
SECTORS = ["MOV","USE","CLI","GPU","LOG","AXM","CTY","MNA","AUR","ZEN","ARC"]
def derive(state):
    a, b = TRITS[state // 3], TRITS[state % 3]
    return {"state": state, "a": a, "b": b,
            "label": a + "*" + b, "score": SCORES[state]}
def continuum729():
    return [{"cell": c, **derive(s)} for c in range(CELLS) for s in range(9)]
def best(cell, grid):
    opts = sorted((derive(s) for s in range(9)), key=lambda d: -d["score"])
    return {"cell": cell, "current": derive(grid[cell]), "options": opts}
def kartor_coverage(registry, level):
    covered = set()
    for o in registry:
        if o["kartor"]["level"] == level and o["kartor"]["weight"] > 0:
            covered.update(o.get("covers", []))
    return round(len(covered) / len(SECTORS) * 100)
def kartor_balance(registry):
    cov = {l: kartor_coverage(registry, l) for l in LEVELS}
    bal = (min(cov.values()) / max(cov.values())) if max(cov.values()) else 0
    pressure = cov[81] - (cov[243] + cov[729]) / 2
    return {"coverage": cov, "balance": round(bal, 2), "pressure": pressure}
STAGES = ["CITY", "ZIP", "BAKE", "PREP", "SCAN", "ATOM"]
def suite_backwards(grid):
    grid = list(grid)
    log = []
    for step, stage in enumerate(reversed(STAGES)):
        chunk = list(range(step * 14 % CELLS, min(CELLS, step * 14 % CELLS + 14)))
        for i in chunk:
            grid[i] = max(0, grid[i] - 3)
        log.append({"stage": stage, "rawed": chunk})
    return {"grid": grid, "log": log,
            "total_score": sum(SCORES[s] for s in grid)}
RECORDS = {}
def records_list(collection, limit=None):
    rows = [r for (c, _), r in RECORDS.items() if c == collection]
    return {"records": rows[:limit] if limit else rows, "next_cursor": None}
def records_create(collection, value):
    rid = "rec_%d" % (len(RECORDS) + 1)
    rec = {"id": rid, "value": value, "created_at": rid, "updated_at": rid}
    RECORDS[(collection, rid)] = rec
    return rec
def records_replace(collection, rid, value):
    rec = RECORDS[(collection, rid)]
    rec["value"] = value
    return rec
ACTIONS = {
    "records.list":    lambda a: records_list(a["collection"], a.get("limit")),
    "records.create":  lambda a: records_create(a["collection"], a["value"]),
    "records.replace": lambda a: records_replace(a["collection"], a["id"], a["value"]),
    "continuum.derive": lambda a: derive(a["state"]),
    "continuum.best":   lambda a: best(a["cell"], a["grid"]),
    "kartor.coverage":  lambda a: kartor_balance(a["registry"]),
    "suite.backwards":  lambda a: suite_backwards(a["grid"]),
}
class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n) or b"{}")
        try:
            payload = {"data": ACTIONS[body["action"]](body.get("args", {}))}
        except Exception as e:
            payload = {"error": str(e)}
        raw = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)
    def do_GET(self):
        path = "rom.html" if self.path in ("/", "/rom.html") else self.path.lstrip("/")
        try:
            raw = open(path, "rb").read()
            self.send_response(200)
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
        except FileNotFoundError:
            self.send_error(404)
    def log_message(self, *a):
        pass
DEMO_REGISTRY = [
    {"kartor": {"level": 81, "flow": "WORK", "sector": "GPU", "weight": 912},
     "covers": ["MOV", "USE", "LOG", "GPU", "CLI"]},
    {"kartor": {"level": 243, "flow": "WORK", "sector": "LOG", "weight": 611},
     "covers": ["LOG", "CLI", "ARC"]},
    {"kartor": {"level": 729, "flow": "MEM", "sector": "ARC", "weight": 115},
     "covers": ["ARC", "LOG"]},
]
def main():
    args = sys.argv[1:]
    if "--print" in args:
        for slot in continuum729():
            print("Zelle %02d  Zustand %d  %-18s Score %.1f"
                  % (slot["cell"], slot["state"], slot["label"], slot["score"]))
    elif "--best" in args:
        cell = int(args[args.index("--best") + 1])
        grid = [(i * 7) % 9 for i in range(CELLS)]
        print(json.dumps(best(cell, grid), indent=2, ensure_ascii=False))
    elif "--pipeline" in args:
        out = suite_backwards([(i * 7) % 9 for i in range(CELLS)])
        for row in out["log"]:
            print("RUECKWAERTS %-5s -> Zellen %s roh" % (row["stage"], row["rawed"]))
        print("Gesamt-Score: %.1f / %d" % (out["total_score"], CELLS * 4))
    elif "--kartor" in args:
        print(json.dumps(kartor_balance(DEMO_REGISTRY), indent=2))
    else:
        print("ROM.os Nutzraum: http://127.0.0.1:8787/rom.html")
        HTTPServer(("127.0.0.1", 8787), Handler).serve_forever()
if __name__ == "__main__":
    main()
ROM.OS · NUTZRAUM CO
