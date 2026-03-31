"""
Piezosystem Jena NV200/D NET — triggered step mode via EPICS IOC.

Loads up to 1024 positions into the arbitrary waveform generator buffer.
Each rising edge on the TRG IN connector (pin 3 of the I/O D-Sub, TTL 0/3.3-5V)
advances the actuator to the next position.

Usage:
    1. Set the PV prefix for each axis (e.g. 'JenaNV200D:jena1').
    2. Define your list of positions in physical units (µm or mrad).
    3. Run the script. The actuator is ready when "Running" is printed.
    4. Each TTL rising edge on TRG IN steps to the next position.
    5. Press Enter to stop and restore manual control.

Notes:
    - Commands are sent via EPICS PVs (<prefix>:write / <prefix>:read),
      so the IOC Telnet connection is reused — no conflict.
    - Requires a sensor-equipped actuator for closed loop (cl=1).
    - Positions must be within the actuator's closed-loop stroke range.
    - gtarb,65535 sets a ~3.3 s auto-advance fallback; in practice the trigger
      drives the steps.
"""

import time
import epics
import numpy as np


class NV200NET:

    def __init__(self, pv_prefix):
        """
        Parameters
        ----------
        pv_prefix : str
            EPICS PV prefix, e.g. 'JenaNV200D:jena1'
            Expects <prefix>:write and <prefix>:read PVs.
        """
        self._pv_write = epics.PV(f'{pv_prefix}:write')
        self._pv_read  = epics.PV(f'{pv_prefix}:read')
        time.sleep(0.2)  # allow CA connection and type detection to complete
        if not self._pv_write.connected:
            raise RuntimeError(f'Cannot connect to {pv_prefix}:write')

    def cmd(self, command):
        """Send a raw ASCII command and return the response."""
        self._pv_write.put(command, wait=True)
        time.sleep(0.05)
        response = self._pv_read.get(as_string=True) or ''
        if response.startswith('error'):
            raise RuntimeError(f'Device error on "{command}": {response}')
        return response

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
        pass  # no socket to close; IOC manages the connection


if __name__ == '__main__':

    ctrl_x = NV200NET('JenaNV200D:jena1')
    ctrl_y = NV200NET('JenaNV200D:jena2')
    try:
        # Passing positions=None auto-generates 1024 steps spanning the full stroke.
        # Or pass your own list: setup_triggered_step(positions=[0, 10, 20, ...])
        print('--- X axis ---')
        ctrl_x.setup_triggered_step(positions=None, n=1024, closed_loop=True)
        print('--- Y axis ---')
        ctrl_y.setup_triggered_step(positions=None, n=1024, closed_loop=True)

        # Uncomment to save positions to EEPROM (load later with ctrl.load_from_eeprom())
        # ctrl_x.save_to_eeprom()
        # ctrl_y.save_to_eeprom()

        input('\nPress Enter to stop...\n')
    finally:
        ctrl_x.stop()
        ctrl_x.close()
        ctrl_y.stop()
        ctrl_y.close()
