import board

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.scanners.digitalio import DigitalScanner
from kmk.extensions.encoder import EncoderHandler


# -------------------------
# Keyboard Object
# -------------------------
keyboard = KMKKeyboard()


# -------------------------
# Buttons (GP26 → GP29)
# -------------------------
keyboard.matrix = [
    DigitalScanner(
        pins=[
            board.GP26,
            board.GP27,
            board.GP28,
            board.GP29,
        ],
        value_when_pressed=False,
    )
]


# -------------------------
# Rotary Encoder
# Pins: (A, B, Button)
# -------------------------
encoder = EncoderHandler()

encoder.pins = (
    (board.GP2, board.GP4, board.GP3),
)

# Encoder works on ALL layers
encoder.map = [
    ((KC.VOLD, KC.VOLU), KC.MUTE),
    ((KC.VOLD, KC.VOLU), KC.MUTE),
    ((KC.VOLD, KC.VOLU), KC.MUTE),
]

keyboard.extensions.append(encoder)


# -------------------------
# Keymap (3 Profiles / Layers)
# -------------------------
keyboard.keymap = [
    # Layer 0 — MEDIA
    [
        KC.TO(1),     # Button 1 → Switch to Layer 1
        KC.MPRV,      # Button 2 → Previous Track
        KC.MPLY,      # Button 3 → Play / Pause
        KC.MNXT,      # Button 4 → Next Track
    ],

    # Layer 1 — EDIT
    [
        KC.TO(2),     # Button 1 → Switch to Layer 2
        KC.CUT,       # Button 2 → Cut
        KC.COPY,      # Button 3 → Copy
        KC.PASTE,     # Button 4 → Paste
    ],

    # Layer 2 — EMPTY / RESET
    [
        KC.TO(0),     # Button 1 → Back to Layer 0
        KC.NO,
        KC.NO,
        KC.NO,
    ],
]


# -------------------------
# Start Keyboard
# -------------------------
if __name__ == "__main__":
    keyboard.go()
