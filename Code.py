"""
Seeed Studio XIAO RP2040 - Media Controller (Not working fully)
=====================================================
Fixes:
  - Double input: buttons now require full press AND release cycle
  - Encoder volume: checked independently from button elif chain
  - OLED: explicit I2C address 0x3C, startup delay, minimal init

Wiring:
  D0  = Play/Pause button
  D1  = Skip Forward button
  D2  = Skip Backward button
  D3  = Hello World button
  D4  = OLED SDA
  D5  = OLED SCL
  D7  = Encoder push button
  D8  = Encoder A
  D10 = Encoder B
  Common wire = GND
"""

import board
import busio
import digitalio
import rotaryio
import time
import usb_hid
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

# ── Wait for USB to settle ────────────────────────────────────────────────────
time.sleep(1)

# ── OLED Setup ────────────────────────────────────────────────────────────────
oled = None
try:
    import adafruit_ssd1306
    i2c = busio.I2C(scl=board.D5, sda=board.D4, frequency=400000)
    time.sleep(0.5)
    oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)
    oled.fill(0)
    oled.text("Hello World!", 16, 28, 1)
    oled.show()
    print("OLED OK - Hello World!")
except Exception as e:
    print("OLED failed:", e)


def show_oled_message(text):
    if oled is None:
        print("OLED unavailable")
        return

    oled.fill(0)
    x = max(0, (128 - len(text) * 8) // 2)
    oled.text(text, x, 28, 1)
    oled.show()

# ── USB HID ───────────────────────────────────────────────────────────────────
cc = ConsumerControl(usb_hid.devices)

# ── Button class: fires once on press, requires release before next press ─────
class Button:
    def __init__(self, pin):
        self._io = digitalio.DigitalInOut(pin)
        self._io.direction = digitalio.Direction.INPUT
        self._io.pull = digitalio.Pull.UP
        self._pressed = False   # True while physically held down

    @property
    def just_pressed(self):
        """Returns True exactly once per physical press."""
        raw = not self._io.value   # True = pressed (active low)
        if raw and not self._pressed:
            self._pressed = True
            return True
        if not raw:
            self._pressed = False
        return False

btn_play  = Button(board.D0)
btn_fwd   = Button(board.D1)
btn_back  = Button(board.D2)
btn_hello = Button(board.D3)
btn_enc   = Button(board.D7)

# ── Rotary Encoder ─────────────────────────────────────────────────────────────
# If volume goes the wrong direction, swap D8 and D10 here:
encoder  = rotaryio.IncrementalEncoder(board.D8, board.D10)
last_step = encoder.position // 4

# ── Main loop ──────────────────────────────────────────────────────────────────
while True:

    # --- Buttons (each fires exactly once per press) ---
    if btn_play.just_pressed:
        cc.send(ConsumerControlCode.PLAY_PAUSE)
        print("Play/Pause")

    if btn_fwd.just_pressed:
        cc.send(ConsumerControlCode.SCAN_NEXT_TRACK)
        print("Skip Forward")

    if btn_back.just_pressed:
        cc.send(ConsumerControlCode.SCAN_PREVIOUS_TRACK)
        print("Skip Backward")

    if btn_hello.just_pressed:
        show_oled_message("Hello World!")
        print("Hello World!")

    if btn_enc.just_pressed:
        cc.send(ConsumerControlCode.MUTE)
        print("Mute")

    # --- Rotary encoder: use one volume event per detent ---
    cur_step = encoder.position // 4
    delta    = cur_step - last_step
    if delta != 0:
        last_step = cur_step
        if delta > 0:
            for _ in range(abs(delta)):
                cc.send(ConsumerControlCode.VOLUME_INCREMENT)
            print("Vol Up", abs(delta))
        else:
            for _ in range(abs(delta)):
                cc.send(ConsumerControlCode.VOLUME_DECREMENT)
            print("Vol Down", abs(delta))

    time.sleep(0.01)
