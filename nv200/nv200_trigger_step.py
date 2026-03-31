"""
Piezosystem Jena NV200/D NET — triggered step mode over Ethernet.

Loads up to 1024 positions into the arbitrary waveform generator buffer.
Each rising edge on the TRG IN connector (pin 3 of the I/O D-Sub, TTL 0/3.3-5V)
advances the actuator to the next position.

Usage:
    1. Set IP to your device's IP address (check via 'IP-Search' tool or DHCP lease).
    2. Define your list of positions in physical units (µm or mrad).
    3. Run the script. The actuator is ready when "Running" is printed.
    4. Each TTL rising edge on TRG IN steps to the next position.
    5. Press Enter to stop and restore manual control.

Notes:
    - Only one Telnet connection at a time is supported by the device.
    - Requires a sensor-equipped actuator for closed loop (cl=1).
    - Positions must be within the actuator's closed-loop stroke range.
    - gtarb,65535 sets a ~3.3 s auto-advance fallback; in practice the trigger
      drives the steps. Increase gtarb if your trigger rate could exceed 0.3 Hz.
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
        # Decode and strip prompt + echoed command
        text = raw.replace(self.PROMPT, b'').decode(errors='replace').strip()
        if text.startswith(command):
            text = text[len(command):].strip()
        if text.startswith('error'):
            raise RuntimeError(f'Device error on "{command}": {text}')
        return text

    def load_positions(self, positions):
        """
        Write positions into the waveform buffer using gparb (physical units: µm or mrad).
        Positions are clamped to [0, 100] % of stroke if you prefer relative units
        use gbarb instead (values 0.0–100.0).
        """
        n = len(positions)
        if n > 1024:
            raise ValueError(f'Maximum 1024 positions, got {n}')
        print(f'Loading {n} positions into buffer...', flush=True)
        for i, pos in enumerate(positions):
            self.cmd(f'gparb,{i},{pos:.4f}')
            if (i + 1) % 128 == 0 or i == n - 1:
                print(f'  {i + 1}/{n}', flush=True)
        print('Buffer loaded.')

    def setup_triggered_step(self, positions, closed_loop=True):
        """
        Configure the device so each rising edge on TRG IN moves to the next position.

        Parameters
        ----------
        positions : list of float
            Positions in physical units (µm or mrad). Max 1024 values.
        closed_loop : bool
            True for closed loop (requires sensor), False for open loop.
        """
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
        # gsave acknowledges with CR LF — wait for prompt
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
        self.cmd('grun,0')     # stop waveform generator
        self.cmd('trgfkt,0')   # disable trigger function
        self.cmd('modsrc,0')   # setpoint back to USB/Ethernet commands
        print('Stopped. Manual control restored.')

    def position(self):
        """Read the current actuator position (µm or mrad in closed loop)."""
        return float(self.cmd('meas'))

    def close(self):
        self.sock.close()


if __name__ == '__main__':

    IP = '192.168.x.x'   # <-- replace with your device IP

    # --- Define your 1024 positions here (in µm or mrad) ---
    # Example: 1024 evenly spaced steps across a 100 µm stroke
    positions = list(np.linspace(0, 100, 1024))

    ctrl = NV200NET(IP)
    try:
        ctrl.setup_triggered_step(positions, closed_loop=True)

        # Uncomment to save positions to EEPROM (load later with ctrl.load_from_eeprom())
        # ctrl.save_to_eeprom()

        input('\nPress Enter to stop...\n')
    finally:
        ctrl.stop()
        ctrl.close()
