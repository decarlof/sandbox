#!/usr/bin/env python3
import argparse
import base64
import http.client
import re
import sys
import time


# Usage: 
# # Check outlet 1 state (prints ON or OFF)
# python pdu.py --ip 10.54.113.66 -u rmtswbma -p sch02bma status 1

# # Turn outlet 1 ON (idempotent: running it again keeps it ON)
# python pdu.py --ip 10.54.113.66 -u rmtswbma -p sch02bma on 1

# # Turn outlet 1 OFF (idempotent: running it again keeps it OFF)
# python pdu.py --ip 10.54.113.66 -u rmtswbma -p sch02bma off 1

# # Toggle outlet 1 (always flips state)
# python pdu.py --ip 10.54.113.66 -u rmtswbma -p sch02bma toggle 1

class NetBooterHTTP:
    def __init__(self, ip, username, password, timeout=10):
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
        """One press of the web UI 'On/Off' button for this outlet."""
        idx = outlet - 1
        # Working format you confirmed:
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
            return True, ""  # already correct; do nothing
        self._toggle_press(outlet)
        time.sleep(0.25)
        new = self.status(outlet)
        if new != want_on:
            return False, f"After toggle got {'ON' if new else 'OFF'}, expected {'ON' if want_on else 'OFF'}"
        return True, ""


def main():
    ap = argparse.ArgumentParser(description="NP-05B HTTP control (toggle + idempotent on/off)")
    ap.add_argument("--ip", required=True)
    ap.add_argument("-u", "--username", required=True)
    ap.add_argument("-p", "--password", required=True)

    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status").add_argument("outlet", type=int, choices=range(1, 6))
    sub.add_parser("toggle").add_argument("outlet", type=int, choices=range(1, 6))
    sub.add_parser("on").add_argument("outlet", type=int, choices=range(1, 6))
    sub.add_parser("off").add_argument("outlet", type=int, choices=range(1, 6))

    args = ap.parse_args()

    nb = NetBooterHTTP(args.ip, args.username, args.password)
    try:
        if args.cmd == "status":
            print("ON" if nb.status(args.outlet) else "OFF")
            return 0

        if args.cmd == "toggle":
            ok, before, after = nb.toggle(args.outlet)
            print(f"{'OK' if ok else 'FAIL'}: {('ON' if before else 'OFF')} -> {('ON' if after else 'OFF')}")
            return 0 if ok else 2

        if args.cmd == "on":
            ok, msg = nb.ensure(args.outlet, True)
        else:  # off
            ok, msg = nb.ensure(args.outlet, False)

        print("OK" if ok else f"FAIL: {msg}")
        return 0 if ok else 2

    finally:
        nb.close()


if __name__ == "__main__":
    sys.exit(main())
