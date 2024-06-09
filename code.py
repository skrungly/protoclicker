import board
import collections
import keypad
import math
import time
import usb_hid

import colorsys
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

# list of integer gamma-correction values for accurate neopixel colours
GAMMA_TABLE = [int(math.pow(i / 255, 2.8) * 255 + 0.5) for i in range(256)]


def gamma_corrected(colour):
    r, g, b = colour
    return GAMMA_TABLE[r], GAMMA_TABLE[g], GAMMA_TABLE[b]


COLOUR_OFF = gamma_corrected((63, 63, 63))

# as the keys are pressed with varying intensity, their
# colour/hue should vary to indicate it
HUE_SLOW = 0.40
HUE_FAST = 0.02
HUE_STEPS = 16

INTENSITY_COLOURS = [
    colorsys.hsv_to_rgb(
        HUE_SLOW + step * (HUE_FAST - HUE_SLOW) / (HUE_STEPS - 1),
        1.0,
        1.0,
    ) for step in range(HUE_STEPS)
]

# how many recent key presses to indicate intensity
RECENT_PRESS_COUNT = 4
INTENSE_KPS = 10

# as the keys are held, their colour should fade.
COLOUR_HOLD = gamma_corrected(colorsys.hsv_to_rgb(0.65, 0.25, 1.0))
FADE_STEPS = 16
FADE_STEP_INTERVAL_NS = (2 * 10 ** 9) // FADE_STEPS  # total 2 seconds

COLOUR_MATRIX = [
    # generate a gradient between the key press colour and
    # the final hold colour, using linear interpolation
    # across the space of RGB colours.
    [
        gamma_corrected(tuple(int(press_colour[i] + step * (
            COLOUR_HOLD[i] - press_colour[i]
        ) / (FADE_STEPS - 1)) for i in range(3)))  # r, g, b
        for step in range(FADE_STEPS)
    ] for press_colour in INTENSITY_COLOURS
]


# end of constants. set up lights and keys!
neopixels = neopixel.NeoPixel(NEOPIXEL_PIN, n=N_KEYS, auto_write=False)
neopixels.fill(COLOUR_OFF)

keys = keypad.Keys(KEY_PINS, value_when_pressed=True, pull=True)
keyboard = Keyboard(usb_hid.devices)

# use deques to keep track of recent press times
keys_intensity = [0] * N_KEYS
recent_presses = tuple(
    collections.deque((), RECENT_PRESS_COUNT) for _ in range(N_KEYS)
)

keys_held_since = [None] * N_KEYS
key_colours = [COLOUR_OFF] * N_KEYS


def calculate_intensity_step(key_presses, time_now):
    if not key_presses:
        key_presses.append(time_now)
        return 0  # first press, not enough info yet

    avg_ns_per_key = (time_now - key_presses[0]) // len(key_presses)
    intensity_step = (HUE_STEPS * 10 ** 9) // (avg_ns_per_key * INTENSE_KPS)

    key_presses.append(time_now)
    return intensity_step


# now begins the event loop
while True:
    time_now = time.monotonic_ns()
    write_pixels = False

    event = keys.events.get()
    if event:
        key = event.key_number

        if event.pressed:
            keyboard.press(KEY_VALUES[key])
            keys_held_since[key] = time_now
            keys_intensity[key] = calculate_intensity_step(
                recent_presses[key], time_now
            )

        if event.released:
            keyboard.release(KEY_VALUES[key])
            keys_held_since[key] = None

            # there isn't any special colour behaviour for
            # released keys, so that can just be set now.
            neopixels[key] = COLOUR_OFF
            write_pixels = True

    for key, held_since in enumerate(keys_held_since):
        if not held_since:
            continue

        current_fade_step = (time_now - held_since) // FADE_STEP_INTERVAL_NS
        fade_index = min(FADE_STEPS - 1, current_fade_step)
        intensity_index = min(HUE_STEPS - 1, keys_intensity[key])

        current_colour = COLOUR_MATRIX[intensity_index][fade_index]

        if neopixels[key] != current_colour:
            neopixels[key] = current_colour
            write_pixels = True

    if write_pixels:
        neopixels.show()
