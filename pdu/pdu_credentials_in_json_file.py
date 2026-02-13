#!/usr/bin/env python3
import argparse
import base64
import http.client
import json
import os
import pathlib
import re
import sys
import time

# Hardcoded credentials file path
CREDENTIALS_FILE_NAME = os.path.join(str(pathlib.Path.home()), "access.json")

# Usage: 
# python pdu_credentials_in_json_file.py --pdu a status 1
# python pdu_credentials_in_json_file.py --pdu a on 1
# python pdu_credentials_in_json_file.py --pdu b off 5
# python pdu_credentials_in_json_file.py --pdu a toggle 1 OK: OFF -> ON or OK: ON -> OFF

def load_pdu_creds(pdu: str):
    """
    Reads PDU credentials from ~/access.json using keys:
      pdu_a_username, pdu_a_password, pdu_a_ip_address
      pdu_b_username, pdu_b_password, pdu_b_ip_address

    Ignores webcam_* keys.
    """
    pdu = pdu.lower()
    if pdu not in ("a", "b"):
        raise ValueError("--pdu must be 'a' or 'b'")

    with open(CREDENTIALS_FILE_NAME, "r") as f:
        cfg = json.load(f)

    prefix = f"pdu_{pdu}_"
    try:
        ip = cfg[prefix + "ip_address"]
        user = cfg[prefix + "username"]
        pwd = cfg[prefix + "password"]
    except KeyError as e:
        raise KeyError(f"Missing key in {CREDENTIALS_FILE_NAME}: {e}")

    return ip, user, pwd


class NetBooterHTTP:
    def __init__(self, ip, username, password, timeout=10):
        self.ip = ip
        self.auth = base64.b64encode(f"{username}:{password}".encode()).decode()
        self.conn = http.client.HTTPConnection(ip, timeout=timeout)

    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass

    def _req(self, method, path, body=b"", headers=None):
        headers = {} if headers is None else dict(headers)
        headers["Authorization"] = f"Basic {self.auth}"
        headers.setdefault("Content-Length", str(len(body)))

        self.conn.putrequest(method, path)
        for k, v in headers.items():
            self.conn.putheader(k, v)
        self.conn.endheaders()
        if body:
            self.conn.send(body)

        resp = self.conn.getresponse()
        data = resp.read().decode(errors="ignore")
        if resp.status != 200:
            raise RuntimeError(f"HTTP {resp.status} {method} {path}: {data[:200]!r}")
        return data

    def status(self, outlet: int) -> bool:
        """Return True=ON, False=OFF for outlet 1..5."""
        if outlet not in (1, 2, 3, 4, 5):
            raise ValueError("outlet must be 1..5")

        xml = self._req("GET", "/status.xml")
        idx = outlet - 1  # outlet 1 -> rly0

        m = re.search(rf"<rly{idx}>([01])</rly{idx}>", xml)
        if not m:
            raise RuntimeError(f"Could not parse /status.xml for outlet {outlet}:\n{xml}")
        return m.group(1) == "1"

    def _toggle_press(self, outlet: int):
        """Press the web UI On/Off button once (toggle)."""
        idx = outlet - 1
        # Working format you validated:
        # POST /cmd.cgi?rly=<idx> with Content-Type: text/plain and body "1"
        self._req(
            "POST",
            f"/cmd.cgi?rly={idx}",
            body=b"1",
            headers={"Content-Type": "text/plain"},
        )

    def toggle(self, outlet: int):
        before = self.status(outlet)
        self._toggle_press(outlet)
        time.sleep(0.25)
        after = self.status(outlet)
        return (after != before), before, after

    def ensure(self, outlet: int, want_on: bool):
        """Idempotent: only toggles if needed."""
        cur = self.status(outlet)
        if cur == want_on:
            return True, ""

        self._toggle_press(outlet)
        time.sleep(0.25)
        new = self.status(outlet)

        if new != want_on:
            return False, f"After toggle got {'ON' if new else 'OFF'}, expected {'ON' if want_on else 'OFF'}"
        return True, ""


def main():
    ap = argparse.ArgumentParser(description=f"NP-05B HTTP control using creds from {CREDENTIALS_FILE_NAME}")
    ap.add_argument("--pdu", required=True, choices=["a", "b", "A", "B"])

    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status").add_argument("outlet", type=int, choices=range(1, 6))
    sub.add_parser("toggle").add_argument("outlet", type=int, choices=range(1, 6))
    sub.add_parser("on").add_argument("outlet", type=int, choices=range(1, 6))
    sub.add_parser("off").add_argument("outlet", type=int, choices=range(1, 6))

    args = ap.parse_args()
    ip, user, pwd = load_pdu_creds(args.pdu)

    nb = NetBooterHTTP(ip, user, pwd)
    try:
        if args.cmd == "status":
            print("ON" if nb.status(args.outlet) else "OFF")
            return 0

        if args.cmd == "toggle":
            ok, before, after = nb.toggle(args.outlet)
            print(f"{'OK' if ok else 'FAIL'}: {('ON' if before else 'OFF')} -> {('ON' if after else 'OFF')}")
            return 0 if ok else 2

        ok, msg = (nb.ensure(args.outlet, True) if args.cmd == "on" else nb.ensure(args.outlet, False))
        print("OK" if ok else f"FAIL: {msg}")
        return 0 if ok else 2

    finally:
        nb.close()


if __name__ == "__main__":
    raise SystemExit(main())
