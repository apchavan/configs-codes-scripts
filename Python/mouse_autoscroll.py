"""
Script to vertically scroll the mouse every 2 seconds, in up & down direction.
It can be used to prevent automatic sleeping when the system is idle.

This uses `pynput` package to control the mouse.
Reference:
[1] https://github.com/moses-palmer/pynput
[2] https://pynput.readthedocs.io/
"""

import time
from pynput.mouse import Controller

mouse_controller: Controller = Controller()
vertical_scroll_pixels: int = 1

while True:
    vertical_scroll_pixels *= -1
    mouse_controller.scroll(0, vertical_scroll_pixels)
    time.sleep(2.0)
