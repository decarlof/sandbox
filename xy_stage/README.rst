XY Stage Wireless Controller
============================

Wireless controller for the Kohzu CYAT-070 XY stage mounted on a rotary stage.
Replaces the slip ring with a battery-powered ESP32 communicating over WiFi,
eliminating mechanical complexity while preserving full motor control capability.

.. contents:: Table of Contents
   :depth: 2
   :local:

Overview
--------

The Kohzu CYAT-070 XY stage is mounted on top of a rotary stage for sample
alignment in tomography experiments. Traditionally, motor control signals are
routed through a slip ring. This project replaces the slip ring with:

- A battery-powered ESP32 mounted on the rotating platform
- WiFi communication between the ESP32 and the control PC
- Wireless battery charging (WiBotic TR-110/OC-110) when the stage is parked
- Oriental Motor CVD503-K drivers for the 5-phase PK523HPMB-C4 stepper motors

The XY stage is used **only during sample alignment** (at 0° and 90°) before
the scan begins. During the scan the motors are de-energized and the stage
holds position mechanically via its lead screw.

System Architecture
-------------------

::

                    FIXED FRAME                    ROTATING PLATFORM
                    ───────────                    ─────────────────

    [PC/Python]
        │ WiFi
        │
        └──────────────────────────────────────────► [ESP32]
                                                        │ 3.3V
                                                        │
                                                  [Buck converter]
                                                    (24V → 3.3V)
                                                        │ 24V
                                                        │
    [WiBotic TR-110] ~~wireless~~ [WiBotic OC-110] ──► [6S LiPo 1000 mAh]
      (fixed to frame)              (on platform)        │
                                                         ├──────────────► [CVD503-K #1] → [PK523 X]
                                                         │   24V
                                                         └──────────────► [CVD503-K #2] → [PK523 Y]


Part List
---------

+----+----------------------+--------------------------------+------+--------------+
| #  | Component            | Part                           | Qty  | Approx Cost  |
+====+======================+================================+======+==============+
| 1  | Microcontroller      | ESP32-WROOM-32 dev board       | 1    | $10          |
+----+----------------------+--------------------------------+------+--------------+
| 2  | Motor driver         | Oriental Motor CVD503-K        | 2    | $150 each    |
+----+----------------------+--------------------------------+------+--------------+
| 3  | Stepper motor        | Oriental Motor PK523HPMB-C4    | 2    | (installed)  |
+----+----------------------+--------------------------------+------+--------------+
| 4  | Battery              | 6S LiPo 1000–1500 mAh          | 1    | $30          |
+----+----------------------+--------------------------------+------+--------------+
| 5  | Battery protection   | 6S LiPo BMS board              | 1    | $10          |
+----+----------------------+--------------------------------+------+--------------+
| 6  | Buck converter       | MP1584 module (24V → 3.3V)     | 1    | $3           |
+----+----------------------+--------------------------------+------+--------------+
| 7  | Wireless charger TX  | WiBotic TR-110                 | 1    |              |
+----+----------------------+--------------------------------+------+--------------+
| 8  | Wireless charger RX  | WiBotic OC-110                 | 1    |              |
+----+----------------------+--------------------------------+------+--------------+
| 9  | Current limit        | 220 Ω resistors                | 6    | $1           |
+----+----------------------+--------------------------------+------+--------------+
| 10 | Battery connector    | XT60                           | 1    | $2           |
+----+----------------------+--------------------------------+------+--------------+
| 11 | Wiring               | 22 AWG stranded wire           | —    | $5           |
+----+----------------------+--------------------------------+------+--------------+

**Total: ~$810**

Motor Specifications
--------------------

+------------------+--------------------------------+
| Parameter        | Value                          |
+==================+================================+
| Model            | Oriental Motor PK523HPMB-C4    |
+------------------+--------------------------------+
| Type             | 5-phase stepper                |
+------------------+--------------------------------+
| Phase current    | 0.75 A                         |
+------------------+--------------------------------+
| Basic step angle | 0.36° (1000 steps/rev)         |
+------------------+--------------------------------+
| Frame size       | NEMA 23 (56.4 mm)              |
+------------------+--------------------------------+

Driver Specifications
---------------------

+------------------+--------------------------------+
| Parameter        | Value                          |
+==================+================================+
| Model            | Oriental Motor CVD503-K        |
+------------------+--------------------------------+
| Motor type       | 5-phase PK series              |
+------------------+--------------------------------+
| Supply voltage   | 24 VDC                         |
+------------------+--------------------------------+
| Output current   | 0.35 A/phase                   |
+------------------+--------------------------------+
| Control input    | Pulse / Direction (TTL)        |
+------------------+--------------------------------+
| Wiring           | New Pentagon                   |
+------------------+--------------------------------+

Battery and Charging
--------------------

**Battery**

- Chemistry: LiPo
- Configuration: 6S (6 cells in series)
- Nominal voltage: 22.2 V
- Full charge voltage: 25.2 V
- Capacity: 1000–1500 mAh
- Approximate size (1000 mAh): 115 × 35 × 25 mm
- Approximate weight (1000 mAh): 155 g

The 6S LiPo voltage range (19.8–25.2 V) is compatible with the CVD503-K
24 V supply requirement and within the WiBotic OC-110 battery voltage range
(7.92–30.1 V).

**Wireless Charging (WiBotic TR-110 / OC-110)**

- The TR-110 transmitter is fixed to the frame at the park position
- The OC-110 receiver is mounted on the rotating platform
- Charging occurs only when the rotary stage is parked (between scans)
- Air gap between transmitter and receiver coils is set at installation
  to match WiBotic specifications

+------------------+--------------------------------+
| Parameter        | OC-110 Value                   |
+==================+================================+
| Battery voltage  | 7.92–30.1 V DC                 |
+------------------+--------------------------------+
| Max charge current | 5 A                          |
+------------------+--------------------------------+
| Max charge power | 90 W                           |
+------------------+--------------------------------+
| Compatible chem. | LiPo, LiIon, LiFePO4, SLA, NMH |
+------------------+--------------------------------+
| Weight (PCB)     | 45 g                           |
+------------------+--------------------------------+
| Communication    | UAVCAN API over CAN-bus        |
+------------------+--------------------------------+

GPIO Pin Assignment
-------------------

+----------+---------+------------------+
| ESP32 GPIO | Signal | CVD503-K pin   |
+==========+=========+==================+
| 14       | X STEP  | PULSE+           |
+----------+---------+------------------+
| 27       | X DIR   | DIR+             |
+----------+---------+------------------+
| 26       | X AWO   | AWO+             |
+----------+---------+------------------+
| 25       | Y STEP  | PULSE+           |
+----------+---------+------------------+
| 33       | Y DIR   | DIR+             |
+----------+---------+------------------+
| 32       | Y AWO   | AWO+             |
+----------+---------+------------------+

Wiring Diagram
--------------

**ESP32 → CVD503-K (repeat for each axis)**

::

    ESP32 (3.3V logic)              CVD503-K
    ──────────────────              ────────
    GPIO_STEP ──[220Ω]──────────► PULSE+
                                   PULSE- ──► GND
    GPIO_DIR  ──[220Ω]──────────► DIR+
                                   DIR-   ──► GND
    GPIO_AWO  ──[220Ω]──────────► AWO+    HIGH = motors OFF
                                   AWO-   ──► GND

.. note::
   The CVD503-K inputs are optically isolated. The 220 Ω resistors limit
   current through the input optocouplers to a safe level for 3.3 V logic.
   AWO (All Windings Off): HIGH de-energizes the motor; the stage holds
   position mechanically via the lead screw.

**Power wiring**

::

    6S LiPo (+) ──────────────────► CVD503-K VDC  (×2)
    6S LiPo (+) ──────────────────► Buck converter IN+
    Buck OUT (3.3V) ───────────────► ESP32 3V3
    6S LiPo (−) ──────────────────► CVD503-K GND  (×2)
    6S LiPo (−) ──────────────────► Buck converter IN−
    Buck OUT GND ──────────────────► ESP32 GND

    WiBotic OC-110 OUT (+) ───────► 6S LiPo (+) via BMS
    WiBotic OC-110 OUT (−) ───────► 6S LiPo (−) via BMS

Software
--------

Repository structure::

    xy_stage/
    ├── README.rst          this file
    ├── xy_stage.py         Python client (runs on PC)
    └── esp32/
        └── main.py         MicroPython firmware (runs on ESP32)

ESP32 Firmware (``esp32/main.py``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Written in MicroPython. On boot the ESP32:

1. Connects to the configured WiFi network
2. Prints its IP address to the serial console
3. Starts a TCP server on port 8080
4. Waits for JSON commands from the Python client
5. De-energizes both motors by default (AWO high)

**Supported commands**

+-------------------+-------------------------------------------------------+
| Command           | Description                                           |
+===================+=======================================================+
| ``move``          | Move one axis N steps at a given speed and direction  |
+-------------------+-------------------------------------------------------+
| ``enable``        | Energize motor(s)                                     |
+-------------------+-------------------------------------------------------+
| ``disable``       | De-energize motor(s) — stage holds position           |
+-------------------+-------------------------------------------------------+
| ``status``        | Return enable state of both axes                      |
+-------------------+-------------------------------------------------------+
| ``sleep``         | Deep sleep ESP32 (wake with reset button)             |
+-------------------+-------------------------------------------------------+

Python Client (``xy_stage.py``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Runs on the control PC. Sends JSON commands to the ESP32 over TCP/WiFi.

Example usage::

    from xy_stage import XYStageController

    stage = XYStageController('192.168.1.50')   # ESP32 IP

    # Align sample at 0 degrees
    stage.move('x', steps=200, direction=1, speed=500)
    stage.move('y', steps=100, direction=0, speed=300)

    # Disable motors before scan (stage holds position)
    stage.disable()

Installation
------------

**Step 1 — Flash MicroPython on the ESP32**

Download the ESP32 MicroPython firmware from https://micropython.org/download/esp32/
then flash it::

    pip install esptool
    esptool.py --port /dev/ttyUSB0 erase_flash
    esptool.py --port /dev/ttyUSB0 write_flash -z 0x1000 esp32-firmware.bin

**Step 2 — Configure WiFi credentials**

Edit ``esp32/main.py`` and set::

    SSID     = 'your_network_name'
    PASSWORD = 'your_wifi_password'

Optionally set a static IP to avoid having to look it up each time::

    STATIC_IP = '192.168.1.50'   # or None for DHCP

**Step 3 — Upload firmware to ESP32**

Using ``ampy``::

    pip install adafruit-ampy
    ampy --port /dev/ttyUSB0 put esp32/main.py

Or use Thonny IDE (https://thonny.org) which provides a graphical file manager
for MicroPython devices.

**Step 4 — Find the ESP32 IP address**

Open a serial terminal (Thonny, screen, minicom) at 115200 baud. On boot
the ESP32 prints::

    WiFi connected — IP: 192.168.1.50
    Listening on 192.168.1.50:8080

**Step 5 — Install Python client dependencies**

No external dependencies — the client uses only the Python standard library::

    python xy_stage.py   # runs the built-in example

**Step 6 — Set the ESP32 IP in the client**

Edit ``xy_stage.py``::

    ESP32_IP = '192.168.1.50'   # IP printed by ESP32 on boot

Operation
---------

Typical scan sequence
~~~~~~~~~~~~~~~~~~~~~

1. Rotary stage moves to **0°** park position
2. WiBotic charges the battery (if needed)
3. Python client sends move commands to align the sample on X and Y
4. Motors are disabled (``stage.disable()``)
5. Rotary stage moves to **90°**
6. Python client sends move commands to verify/adjust alignment
7. Motors are disabled
8. **Scan begins** — ESP32 in idle state, motors off, stage holds position
9. Scan ends — rotary stage returns to park position
10. WiBotic charges the battery for the next session

Power budget
~~~~~~~~~~~~

+----------------------+------------------+------------------+
| Component            | Current (active) | Current (idle)   |
+======================+==================+==================+
| ESP32 (WiFi active)  | ~240 mA @ 3.3 V  | ~10 mA (idle)    |
+----------------------+------------------+------------------+
| CVD503-K × 2        | ~1.4 A @ 24 V    | 0 A (AWO off)    |
+----------------------+------------------+------------------+
| Buck converter loss  | ~5%              | —                |
+----------------------+------------------+------------------+

A 1000 mAh 6S LiPo provides sufficient energy for multiple alignment
sessions per charge. Wireless charging between scans keeps the battery
topped up during normal operation.

Notes
-----

- Only one TCP connection is handled at a time by the ESP32 server
- The CVD503-K DIP switches set microstepping resolution — consult the
  CVD503-K manual to match your desired steps/mm for the CYAT-070
- The lead screw of the CYAT-070 is self-locking at the rotation speeds
  used (50°/s = 8.3 RPM); centrifugal force at this speed is negligible
  (~0.019 N for a 0.5 kg load at 50 mm radius)
- Motors are de-energized by default on ESP32 boot as a safety measure

References
----------

- Kohzu CYAT-070 stage: https://www.kohzu.co.jp
- Oriental Motor PK523HPMB-C4 datasheet: https://www.orientalmotor.com
- Oriental Motor CVD503-K manual: https://www.orientalmotor.com
- MicroPython ESP32: https://micropython.org/download/esp32/
- WiBotic TR-110 / OC-110: https://wibotic.com
- Thonny IDE: https://thonny.org
