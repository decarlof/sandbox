"""
Python client — Wireless XY Stage Controller
Kohzu CYAT-070 with Oriental Motor PK523HPMB-C4 + CVD503-K drivers

Communicates with the ESP32 firmware (esp32/main.py) over WiFi via TCP.

Usage:
    stage = XYStageController('192.168.1.50')  # ESP32 IP printed on boot
    stage.move('x', steps=200, direction=1, speed=500)
    stage.move('y', steps=100, direction=0, speed=300)
    stage.disable()
"""

import socket
import json


class XYStageController:

    def __init__(self, ip, port=8080, timeout=10.0):
        """
        Parameters
        ----------
        ip      : str   IP address printed by the ESP32 on boot
        port    : int   must match PORT in esp32/main.py (default 8080)
        timeout : float socket timeout in seconds
        """
        self.ip      = ip
        self.port    = port
        self.timeout = timeout

    def _send(self, cmd_dict):
        """Send a command dict and return the response dict."""
        with socket.socket() as s:
            s.settimeout(self.timeout)
            s.connect((self.ip, self.port))
            s.sendall(json.dumps(cmd_dict).encode())
            response = s.recv(1024).decode()
        return json.loads(response)

    def move(self, axis, steps, direction=1, speed=500):
        """
        Move one axis.

        Parameters
        ----------
        axis      : 'x' or 'y'
        steps     : number of steps
        direction : 1 = forward, 0 = reverse
        speed     : steps/second (default 500)
        """
        return self._send({
            'cmd'      : 'move',
            'axis'     : axis,
            'steps'    : steps,
            'direction': direction,
            'speed'    : speed,
        })

    def enable(self, axis=None):
        """Energize motors. axis=None enables both."""
        cmd = {'cmd': 'enable'}
        if axis:
            cmd['axis'] = axis
        return self._send(cmd)

    def disable(self, axis=None):
        """De-energize motors. Stage holds position via lead screw. axis=None disables both."""
        cmd = {'cmd': 'disable'}
        if axis:
            cmd['axis'] = axis
        return self._send(cmd)

    def status(self):
        """Return motor enable state for both axes."""
        return self._send({'cmd': 'status'})

    def sleep(self):
        """Put ESP32 into deep sleep (wake with reset button)."""
        return self._send({'cmd': 'sleep'})


# -----------------------------------------------------------------
# Example usage
# -----------------------------------------------------------------
if __name__ == '__main__':

    ESP32_IP = '192.168.x.x'   # <-- replace with IP printed by ESP32 on boot

    stage = XYStageController(ESP32_IP)

    print('Status:', stage.status())

    # Align sample: move X forward 200 steps at 500 steps/s
    print(stage.move('x', steps=200, direction=1, speed=500))

    # Move Y backward 100 steps at 300 steps/s
    print(stage.move('y', steps=100, direction=0, speed=300))

    # Disable both motors (stage holds position mechanically)
    print(stage.disable())

    print('Status:', stage.status())
