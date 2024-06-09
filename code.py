import board
import keypad
import math
import time
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

COLOUR_OFF = (63, 63, 63)

# as the keys are held, their colour should fade.
COLOUR_PRESS = (63, 255, 0)
COLOUR_HOLD = (0, 63, 255)

FADE_STEPS = 16
FADE_STEP_INTERVAL_NS = (2 * 10 ** 9) // FADE_STEPS  # total 2 seconds

COLOUR_MATRIX = [
    # generate a gradient between the key press colour and
    # the final hold colour, using linear interpolation
    # across the space of RGB colours.
    tuple(int(COLOUR_PRESS[i] + step * (
        COLOUR_HOLD[i] - COLOUR_PRESS[i]
    ) / (FADE_STEPS - 1)) for i in range(3))  # r, g, b
    for step in range(FADE_STEPS)
]

# list of integer gamma-correction values for accurate neopixel colours
GAMMA_TABLE = [int(math.pow(i / 255, 2.8) * 255 + 0.5) for i in range(256)]


def gamma_corrected(colour):
    r, g, b = colour
    return GAMMA_TABLE[r], GAMMA_TABLE[g], GAMMA_TABLE[b]


# end of constants. set up lights and keys!
neopixels = neopixel.NeoPixel(NEOPIXEL_PIN, n=N_KEYS, auto_write=False)
neopixels.fill(COLOUR_OFF)

keys = keypad.Keys(KEY_PINS, value_when_pressed=True, pull=True)
keyboard = Keyboard(usb_hid.devices)

keys_pressed = [None] * N_KEYS
key_colours = [COLOUR_OFF] * N_KEYS

# now begins the event loop
while True:
    time_now = time.monotonic_ns()
    write_pixels = False

    event = keys.events.get()
    if event:
        key = event.key_number

        if event.pressed:
            keyboard.press(KEY_VALUES[key])
            keys_pressed[key] = time_now
            # the colour for pressed keys is handled below

        if event.released:
            keyboard.release(KEY_VALUES[key])
            keys_pressed[key] = None
            neopixels[key] = COLOUR_OFF
            write_pixels = True

    for key, held_since in enumerate(keys_pressed):
        if not held_since:
            continue

        current_fade_step = (time_now - held_since) // FADE_STEP_INTERVAL_NS
        current_colour = COLOUR_MATRIX[min(FADE_STEPS - 1, current_fade_step)]

        if neopixels[key] != current_colour:
            neopixels[key] = current_colour
            write_pixels = True

    if write_pixels:
        neopixels.show()
