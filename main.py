import board

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.scanners.digitalio import DigitalScanner


keyboard = KMKKeyboard()

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

keyboard.keymap = [
    [KC.A, KC.B, KC.C, KC.D],
]

if __name__ == "__main__":
    keyboard.go()
