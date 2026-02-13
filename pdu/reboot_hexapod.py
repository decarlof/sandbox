#!/usr/bin/env python3
"""
Usage
-----

Reboot hexapod controller (power-cycled via PDU outlet 4) and restart its EPICS IOC.

Prereqs:
  - Credentials file exists: ~/access.json
      Must contain keys:
        pdu_a_ip_address, pdu_a_username, pdu_a_password
        pdu_b_ip_address, pdu_b_username, pdu_b_password
      (webcam_* keys may also be present; they are ignored)

  - You can SSH to the IOC host without interactive password prompts
      ssh 2bmb@arcturus

  - EPICS command-line tools available on the machine running this script:
      caget, caput

Examples:
  # Reboot using PDU "a" (reads pdu_a_* from ~/access.json)
  python reboot_hexapod.py --pdu a

  # Reboot using PDU "b"
  python reboot_hexapod.py --pdu b

  # Customize waits (seconds)
  python reboot_hexapod.py --pdu a --off-wait 90 --on-wait 90

  # Increase PV enable verification timeout
  python reboot_hexapod.py --pdu a --enable-timeout 300
"""

import argparse
import base64
import http.client
import json
import os
import pathlib
import re
import subprocess
import time


# -------------------- Local config --------------------

# Hardcoded credentials file path
CREDENTIALS_FILE_NAME = os.path.join(str(pathlib.Path.home()), "access.json")

# IOC control (from your bash examples)
REMOTE_USER = "2bmb"
REMOTE_HOST = "arcturus"
WORK_DIR = "/net/s2dserv/xorApps/epics/synApps_6_3/ioc/2bmHXP/iocBoot/ioc2bmHXP/softioc/"
IOC_CTL = "./2bmHXP.pl"

# EPICS PVs
PV_ALL_ENABLED = "2bmHXP:HexapodAllEnabled.VAL"
PV_ENABLE_WORK = "2bmHXP:EnableWork.PROC"

# Hexapod controller power is on outlet 4
HEXAPOD_OUTLET = 4


# -------------------- Helpers --------------------

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
    ip = cfg[prefix + "ip_address"]
    user = cfg[prefix + "username"]
    pwd = cfg[prefix + "password"]
    return ip, user, pwd


class NetBooterHTTP:
    """
    Synaccess NP-05B (your firmware):
      - Outlet control is a TOGGLE button in the web UI.
      - Toggling is done by:
            POST /cmd.cgi?rly=<idx>
            Content-Type: text/plain
            body: "1"
      - Status is read from:
            GET /status.xml
            <rly0>..</rly0> corresponds to outlet 1, etc.
    """
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
        if outlet not in (1, 2, 3, 4, 5):
            raise ValueError("outlet must be 1..5")

        xml = self._req("GET", "/status.xml")
        idx = outlet - 1  # outlet 1 -> rly0
        m = re.search(rf"<rly{idx}>([01])</rly{idx}>", xml)
        if not m:
            raise RuntimeError(f"Could not parse /status.xml for outlet {outlet}:\n{xml}")
        return m.group(1) == "1"

    def _toggle_press(self, outlet: int):
        idx = outlet - 1
        self._req(
            "POST",
            f"/cmd.cgi?rly={idx}",
            body=b"1",
            headers={"Content-Type": "text/plain"},
        )

    def ensure(self, outlet: int, want_on: bool, verify_delay=0.25) -> bool:
        """
        Idempotent ON/OFF:
          - If already in desired state: do nothing
          - Otherwise press toggle once and verify
        """
        cur = self.status(outlet)
        if cur == want_on:
            return True
        self._toggle_press(outlet)
        time.sleep(verify_delay)
        return self.status(outlet) == want_on

    def on(self, outlet: int) -> bool:
        return self.ensure(outlet, True)

    def off(self, outlet: int) -> bool:
        return self.ensure(outlet, False)


def run_ssh(remote_cmd: str):
    """
    Run a command on arcturus using system ssh.
    Assumes non-interactive auth (keys/agent) is configured.
    """
    return subprocess.run(
        ["ssh", "-t", f"{REMOTE_USER}@{REMOTE_HOST}", remote_cmd],
        check=True,
    )


def ioc_stop():
    cmd = f"cd {WORK_DIR} && source set_epics_arch.sh && {IOC_CTL} stop"
    return run_ssh(cmd)


def ioc_start():
    cmd = f"cd {WORK_DIR} && source set_epics_arch.sh && {IOC_CTL} run"
    return run_ssh(cmd)


def caget(pv: str) -> str:
    # Requires EPICS tools in PATH
    return subprocess.check_output(["caget", "-t", pv], text=True).strip()


def caput(pv: str, value):
    subprocess.check_call(["caput", pv, str(value)])


def wait_for_all_enabled(timeout_s=180, poll_s=2) -> bool:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            if caget(PV_ALL_ENABLED) == "1":
                return True
        except Exception:
            pass
        time.sleep(poll_s)
    return False


# -------------------- Main procedure --------------------

def main():
    ap = argparse.ArgumentParser(
        description=f"Hexapod reboot: stop IOC, power-cycle outlet {HEXAPOD_OUTLET}, start IOC, verify EPICS enabled"
    )
    ap.add_argument("--pdu", required=True, choices=["a", "b", "A", "B"], help="Select PDU creds from ~/access.json")
    ap.add_argument("--off-wait", type=int, default=60, help="Seconds to wait after power OFF")
    ap.add_argument("--on-wait", type=int, default=60, help="Seconds to wait after power ON")
    ap.add_argument("--enable-timeout", type=int, default=180, help="Seconds to wait for HexapodAllEnabled=1")
    args = ap.parse_args()

    ip, user, pwd = load_pdu_creds(args.pdu)
    pdu = NetBooterHTTP(ip, user, pwd)

    try:
        print("Stopping hexapod IOC...")
        ioc_stop()

        print(f"Powering OFF hexapod controller (outlet {HEXAPOD_OUTLET})...")
        if not pdu.off(HEXAPOD_OUTLET):
            raise RuntimeError("PDU power OFF failed (state did not become OFF)")

        print(f"Waiting {args.off_wait}s...")
        time.sleep(args.off_wait)

        print(f"Powering ON hexapod controller (outlet {HEXAPOD_OUTLET})...")
        if not pdu.on(HEXAPOD_OUTLET):
            raise RuntimeError("PDU power ON failed (state did not become ON)")

        print(f"Waiting {args.on_wait}s...")
        time.sleep(args.on_wait)

        print("Starting hexapod IOC...")
        ioc_start()

        print(f"Waiting for {PV_ALL_ENABLED}=1 (timeout {args.enable_timeout}s)...")
        if not wait_for_all_enabled(timeout_s=args.enable_timeout, poll_s=2):
            print(f"{PV_ALL_ENABLED} is not 1; issuing {PV_ENABLE_WORK}=1 and waiting again...")
            caput(PV_ENABLE_WORK, 1)
            if not wait_for_all_enabled(timeout_s=args.enable_timeout, poll_s=2):
                raise RuntimeError(f"{PV_ALL_ENABLED} did not become 1 within timeout")

        print("OK: Hexapod is enabled (HexapodAllEnabled=1).")
        return 0

    finally:
        pdu.close()


if __name__ == "__main__":
    raise SystemExit(main())
