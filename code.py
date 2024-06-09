import board
import keypad
import math
import usb_hid

import neopixel
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

NEOPIXEL_PIN = board.GP0
KEY_PINS = (  # from left to right
    board.GP3,
    board.GP5,
    board.GP6,
    board.GP8,
)

KEY_VALUES = (
    Keycode.D,
    Keycode.F,
    Keycode.J,
    Keycode.K,
)

N_KEYS = len(KEY_PINS)

COLOUR_OFF = 0x3f3f3f
COLOUR_ON = 0xffffff

# list of integer gamma-correction values for accurate neopixel colours
GAMMA_TABLE = [int(math.pow(i / 255, 2.8) * 255 + 0.5) for i in range(256)]


def gamma_corrected(colour):
    r = (colour & 0xff0000) >> 16
    g = (colour & 0x00ff00) >> 8
    b = colour & 0x0000ff

    return (GAMMA_TABLE[r] << 16) + (GAMMA_TABLE[g] << 8) + GAMMA_TABLE[b]


# end of constants. set up lights an keys!
neopixels = neopixel.NeoPixel(NEOPIXEL_PIN, n=N_KEYS)
neopixels.fill(COLOUR_OFF)

keys = keypad.Keys(KEY_PINS, value_when_pressed=True, pull=True)
keyboard = Keyboard(usb_hid.devices)

# now begins the event loop
while True:
    event = keys.events.get()

    if event:
        key = event.key_number

        if event.pressed:
            keyboard.press(KEY_VALUES[key])
            neopixels[key] = gamma_corrected(COLOUR_ON)

        if event.released:
            keyboard.release(KEY_VALUES[key])
            neopixels[key] = gamma_corrected(COLOUR_OFF)
