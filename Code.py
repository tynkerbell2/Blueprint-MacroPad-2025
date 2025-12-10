
import board
import busio
import time

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC

from kmk.scanners.digitalio import DigitalScanner
from kmk.extensions.encoder import EncoderHandler
from kmk.extensions.display import Display
from kmk.extensions.display.ssd1306 import SSD1306


# Keyboard + I2C OLED
keyboard = KMKKeyboard()
i2c = busio.I2C(board.GP7, board.GP6)

display = Display(
    SSD1306(
        i2c=i2c,
        width=128,
        height=32,
        addr=0x3C,
    )
)

keyboard.extensions.append(display)



# Rotary Encoder (GP2, GP4, GP3)
encoder = EncoderHandler()
encoder.pins = (
    (board.GP2, board.GP4, board.GP3),
)

encoder.map = [
    ((KC.VOLD, KC.VOLU), KC.MUTE)
]

keyboard.extensions.append(encoder)


# Buttons (GP26 → SW1 … GP29 → SW4)
keyboard.matrix = [
    DigitalScanner(
        pins=[board.GP26, board.GP27, board.GP28, board.GP29],
        value_when_pressed=False,
    )
]



# Profiles
PROFILE_NAMES = ["MEDIA", "EDIT", "EMPTY"]

keyboard.keymap = [
    # Profile 0 — MEDIA
    [KC.TO(1), KC.MPRV, KC.MPLY, KC.MNXT],
    # Profile 1 — EDITING
    [KC.TO(2), KC.CUT, KC.COPY, KC.PASTE],
    # Profile 2 — EMPTY
    [KC.TO(0), KC.NO, KC.NO, KC.NO],
]


# Track state for UI
volume_steps = 50
last_encoder_pos = 0
last_layer = 0
scroll_offset = 0
scroll_active = True
scroll_timer = 0


# Pixel Art Scorpion (8×8)
# Two-frame “idle blink”
SCORPION_1 = [
    0b00110000,
    0b01111000,
    0b11111100,
    0b11101100,
    0b01111000,
    0b00110000,
    0b01110000,
    0b01010000,
]

SCORPION_2 = [
    0b00110000,
    0b01101000,
    0b11111100,
    0b11101100,
    0b01111000,
    0b00110000,
    0b01110000,
    0b01010000,
]

scorpion_frame = 0
frame_timer = 0


def draw_scorpion(disp, x, y):
    frame = SCORPION_1 if scorpion_frame == 0 else SCORPION_2
    for row, byte in enumerate(frame):
        for col in range(8):
            if byte & (1 << (7 - col)):
                disp.pixel(x + col, y + row, 1)



# OLED Draw Function
def draw_ui(disp, state):
    global scroll_offset, scroll_active, scroll_timer
    global scorpion_frame, frame_timer

    disp.fill(0)

    # Layer change → trigger scrolling banner
    if state.layer != last_layer:
        scroll_active = True
        scroll_offset = 128
        scroll_timer = time.monotonic()

    # Scrolling banner at top
    if scroll_active:
        banner = f"<< {PROFILE_NAMES[state.layer]} MODE >>"
        disp.text(banner, scroll_offset, 0)
        if time.monotonic() - scroll_timer > 0.02:
            scroll_offset -= 2
            scroll_timer = time.monotonic()

        if scroll_offset < -len(banner) * 6:
            scroll_active = False
    else:
        disp.text(f"Profile: {PROFILE_NAMES[state.layer]}", 0, 0)

    # Volume bar
    disp.text("Vol:", 0, 14)
    disp.rect(28, 14, int(volume_steps), 8, 1, fill=True)

    # Scorpion mascot bottom right
    frame_timer += 1
    if frame_timer > 20:  # slow animation
        scorpion_frame = 1 - scorpion_frame
        frame_timer = 0

    draw_scorpion(disp, 112, 20)

    disp.show()


display.draw = draw_ui


# Encoder → Update local volume bar
def after_hid_send(kbd):
    global volume_steps, last_encoder_pos
    pos = encoder.encoders[0].position

    if pos != last_encoder_pos:
        delta = pos - last_encoder_pos
        volume_steps += delta * 2
        volume_steps = max(0, min(100, volume_steps))
        last_encoder_pos = pos

keyboard.after_hid_send = after_hid_send



# Track last layer
def before_matrix_scan(kbd):
    global last_layer
    last_layer = kbd.active_layers[0]

keyboard.before_matrix_scan = before_matrix_scan


# Boot Logo
def show_boot_logo():
    display.driver.fill(0)
    display.driver.text(" SCORPION OS ", 10, 12)
    display.driver.show()
    time.sleep(1.5)

show_boot_logo()



# Start
if __name__ == "__main__":
    keyboard.go()
