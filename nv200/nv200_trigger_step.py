"""
Piezosystem Jena NV200/D NET — triggered step mode over Ethernet (Telnet).

Loads up to 1024 positions into the arbitrary waveform generator buffer.
Each rising edge on the TRG IN connector (pin 3 of the I/O D-Sub, TTL 0/3.3-5V)
advances the actuator to the next position.

Usage:
    1. Stop the EPICS IOC (only one Telnet connection allowed at a time).
    2. Run this script.
    3. Each TTL rising edge on TRG IN steps to the next position.
    4. Press Enter to stop and restore manual control, then restart the IOC.

Notes:
    - Requires a sensor-equipped actuator for closed loop (cl=1).
    - Positions must be within the actuator's closed-loop stroke range.
    - gtarb,65535 sets a ~3.3 s auto-advance fallback; in practice the trigger
      drives the steps.
"""

import socket
import time
import numpy as np


class NV200NET:
    PROMPT = b'NV200/D NET>'

    def __init__(self, ip, port=23, timeout=10.0):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(timeout)
        self.sock.connect((ip, port))
        self._read_until_prompt()  # consume banner/prompt on connect

    def _read_until_prompt(self, timeout=5.0):
        buf = b''
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                chunk = self.sock.recv(256)
                if chunk:
                    # Strip Telnet IAC negotiation bytes (0xFF sequences)
                    chunk = bytes(b for b in chunk if b < 0xFF)
                    buf += chunk
                    if self.PROMPT in buf:
                        return buf
            except socket.timeout:
                break
        return buf

    def cmd(self, command):
        """Send a command, wait for the prompt, and return the response text."""
        self.sock.sendall((command + '\r').encode())
        raw = self._read_until_prompt()
        # Strip null bytes, prompt, then decode
        raw = raw.replace(b'\x00', b'').replace(self.PROMPT, b'')
        text = raw.decode(errors='replace').strip()
        # Strip echoed command prefix (device echoes e.g. "posmin,0.000")
        if text.startswith(command):
            text = text[len(command):].strip()
        # Strip leading comma (response format is "command,value")
        text = text.lstrip(',').strip()
        if text.startswith('error'):
            raise RuntimeError(f'Device error on "{command}": {text}')
        return text

    def stroke(self):
        """Return (posmin, posmax) in physical units as reported by the device."""
        posmin = float(self.cmd('posmin'))
        posmax = float(self.cmd('posmax'))
        return posmin, posmax

    def linspace_positions(self, n=1024):
        """Return n evenly spaced positions spanning the full actuator stroke."""
        posmin, posmax = self.stroke()
        print(f'Actuator stroke: {posmin} … {posmax} (physical units)')
        return list(np.linspace(posmin, posmax, n))

    def load_positions(self, positions):
        """Write positions into the waveform buffer (physical units: µm or mrad)."""
        n = len(positions)
        if n > 1024:
            raise ValueError(f'Maximum 1024 positions, got {n}')
        print(f'Loading {n} positions into buffer...', flush=True)
        for i, pos in enumerate(positions):
            self.cmd(f'gparb,{i},{pos:.4f}')
            if (i + 1) % 128 == 0 or i == n - 1:
                print(f'  {i + 1}/{n}', flush=True)
        print('Buffer loaded.')

    def setup_triggered_step(self, positions=None, n=1024, closed_loop=True):
        """
        Configure the device so each rising edge on TRG IN moves to the next position.

        Parameters
        ----------
        positions : list of float or None
            Positions in physical units (µm or mrad). Max 1024 values.
            If None, n evenly spaced positions spanning the full stroke are used.
        n : int
            Number of positions to generate when positions=None.
        closed_loop : bool
            True for closed loop (requires sensor), False for open loop.
        """
        if positions is None:
            positions = self.linspace_positions(n)

        # Validate against device stroke limits
        posmin, posmax = self.stroke()
        out_of_range = [p for p in positions if p < posmin or p > posmax]
        if out_of_range:
            raise ValueError(
                f'{len(out_of_range)} position(s) outside actuator range '
                f'[{posmin}, {posmax}]: e.g. {out_of_range[0]}'
            )

        n = len(positions)

        # Control mode
        self.cmd(f'cl,{1 if closed_loop else 0}')

        # Waveform generator range
        self.cmd('gsarb,0')           # loop start index
        self.cmd(f'gearb,{n - 1}')   # loop end index
        self.cmd('goarb,0')           # first-cycle start index
        self.cmd('gtarb,65535')       # hold time per step: 65535 × 50 µs ≈ 3.3 s
        self.cmd('gcarb,0')           # 0 = run indefinitely

        # Load the position table
        self.load_positions(positions)

        # Trigger input: each rising edge increments the waveform index by 1
        self.cmd('trgfkt,2')

        # Setpoint source: arbitrary waveform generator
        self.cmd('modsrc,3')

        # Start the waveform generator (begins at goarb = 0)
        self.cmd('grun,1')

        print(f'\nRunning. {n} positions loaded.')
        print('Each rising edge on TRG IN (I/O connector pin 3) steps to the next position.')

    def save_to_eeprom(self):
        """Persist the waveform buffer to EEPROM (survives power cycles)."""
        print('Saving buffer to EEPROM...')
        self.sock.sendall(b'gsave\r')
        self._read_until_prompt(timeout=15.0)
        print('Saved.')

    def load_from_eeprom(self):
        """Restore a previously saved waveform buffer from EEPROM."""
        print('Loading buffer from EEPROM...')
        self.sock.sendall(b'gload\r')
        self._read_until_prompt(timeout=15.0)
        print('Loaded.')

    def stop(self):
        """Stop the waveform generator and restore direct command control."""
        self.cmd('grun,0')
        self.cmd('trgfkt,0')
        self.cmd('modsrc,0')
        print('Stopped. Manual control restored.')

    def position(self):
        """Read the current actuator position (µm or mrad in closed loop)."""
        return float(self.cmd('meas'))

    def close(self):
        self.sock.close()


if __name__ == '__main__':

    IP_X = '10.54.113.126'
    IP_Y = '10.54.113.125'

    ctrl_x = NV200NET(IP_X)
    ctrl_y = NV200NET(IP_Y)
    try:
        # Passing positions=None auto-generates 1024 steps spanning the full stroke.
        # Or pass your own list: setup_triggered_step(positions=[0, 10, 20, ...])
        print('--- X axis ---')
        ctrl_x.setup_triggered_step(positions=None, n=1024, closed_loop=True)
        print('--- Y axis ---')
        ctrl_y.setup_triggered_step(positions=None, n=1024, closed_loop=True)

        # Uncomment to save to EEPROM (persists across power cycles)
        # ctrl_x.save_to_eeprom()
        # ctrl_y.save_to_eeprom()

        input('\nPress Enter to stop...\n')
    finally:
        ctrl_x.stop()
        ctrl_x.close()
        ctrl_y.stop()
        ctrl_y.close()
