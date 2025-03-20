
# MicroPython class for OV2640 Camera

This is a basic interface to the [ArduCAM OV2640](http://www.arducam.com/camera-modules/2mp-ov2640/) under MicroPython for the Raspberry Pi PICO RP2040. This is largely based off of namato's repo of the same name.

Using this class you can:
* Initiate still pictures up to 1600x1200 resolution
* Read them from the camera

## Usage - Hardware Setup

This particular camera has both an i2c and spi interface for setup and
getting data on/off the camera.  A good way to wire up the camera to
the PICO RP2040 is as follows (note Vcc and GND pins are not included here):

 Camera Pin | PICO Pin     |
| --------- | ------------ |
| CS        | GPI17        |
| MOSI      | GPI19        |
| MISO      | GPI16        |
| SCK       | GPI18        |
| SDA       | GPI26        |
| SCL       | GPI27        |

## Usage - Software

First upload the module 'ov2640.py' into the root filesystem on the
PICO board you are using. I used [Thonny](https://thonny.org/).

First download the latest MicroPython [image from here](http://micropython.org/download#esp8266).

Then initialize and capture still frames using code like this.  The included `main.py` contains an example.

You can then retrieve the image off of the board, upload it to a server, etc.

## Credits
Original code was modified from [namato](https://github.com/namato/micropython-ov2640)

The original driver source from Arducam was instrumental in the creation of this pure
MicroPython version.

The overall project was inspired by
[esparducam](https://johan.kanflo.com/building-the-esparducam/), but
getting this to work doesn't require any SMD soldering. :)

