# protoclicker
the circuitpython code for my 4-key osu! protoclicker on a breadboard. this repo
exists primarily for the sake of documentation, so that i can recreate the project
from scratch whenever i want!

## requirements

### hardware

- raspberry pi pico
- micro USB cable capable of data transfer
- 2 half-size breadboards
- a bunch of breadboard jumper wires
- 4 [adafruit neokey socket breakout boards](https://www.adafruit.com/product/4978)
- 4 mechanical switches and keycaps

some soldering is required to add the header pins to the neokey breakout boards!

i would also highly recommend using some form of adhesive to firmly fix the switches
to their sockets (the adafruit product page recommends hot glue or epoxy, but i just
used superglue). without it, the keys will wobble around during gameplay which can
introduce a feeling of inconsistency, and the switches may also fall out or even
snap off their pins entirely.

### software

- adafruit circuitpython loaded on the pi pico (i used version 8.2.9)
- the following libraries from the [adafruit bundle](https://github.com/adafruit/Adafruit_CircuitPython_Bundle):
  * adafruit_hid
  * neopixel

when cloning this repository, ensure that `code.py` is located at the root of the
`CIRCUITPY` filesystem, and that a `lib` folder exists next to it containing the
above libraries.

## breadboard wiring

the neopixels are controlled with pin 0, and the switch cathodes are connected to
pins 3, 5, 6 and 8 (from left to right).

i personally found it more comfortable to have the keys positioned at a slight angle
since the keys for each hand are so close together, but the wiring leaves enough
space to put them in a straight line if desired.

![fritzing wiring diagram](https://github.com/skrungly/protoclicker/assets/37349466/edfddc6e-d2ac-45e9-ab89-7b409f13989b)
