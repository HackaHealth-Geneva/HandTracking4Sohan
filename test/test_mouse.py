# Tested on Windows XP, run from Administrator

import ctypes
import math
import time

from ctypes import c_long, POINTER, sizeof, c_int
from ctypes.wintypes import DWORD

# Select native Win32 API function to use with ctypes.
# https://msdn.microsoft.com/ru-ru/library/windows/desktop/ms648394%28v=vs.85%29.aspx
set_cursor_pos_func = ctypes.windll.user32.SetCursorPos
# https://msdn.microsoft.com/ru-RU/library/windows/desktop/ms646310%28v=vs.85%29.aspx
send_input_func = ctypes.windll.user32.SendInput

# Define required native structures.

# https://msdn.microsoft.com/ru-RU/library/windows/desktop/ms646270%28v=vs.85%29.aspx
# typedef struct tagMOUSEINPUT {
#   LONG      dx;
#   LONG      dy;
#   DWORD     mouseData;
#   DWORD     dwFlags;
#   DWORD     time;
#   ULONG_PTR dwExtraInfo;
# } MOUSEINPUT, *PMOUSEINPUT;
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", c_long),
        ("dy", c_long),
        ("mouseData", DWORD),
        ("dwFlags", DWORD),
        ("time", DWORD),
        ("dwExtraInfo", POINTER(c_long)),
    ]

# https://msdn.microsoft.com/ru-RU/library/windows/desktop/ms646270%28v=vs.85%29.aspx
# typedef struct tagINPUT {
#   DWORD type;
#   union {
#     MOUSEINPUT    mi;
#     KEYBDINPUT    ki;
#     HARDWAREINPUT hi;
#   };
# } INPUT, *PINPUT;
class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", DWORD),
        ("mi", MOUSEINPUT),
    ]

# Define required native Win32 API constants

INPUT_MOUSE = 0

# https://msdn.microsoft.com/ru-RU/library/windows/desktop/ms646273%28v=vs.85%29.aspx
MOUSEEVENTF_MOVE     = 0x001
MOUSEEVENTF_LEFTDOWN = 0x002
MOUSEEVENTF_LEFTUP   = 0x004

# In eternal loop
last_click = time.clock()
while True:                                          
    # Move mouse position according to Lissajous curve
    # (https://en.wikipedia.org/wiki/Lissajous_curve)
    t = time.clock()
    x = 300 + 300 * math.sin(5 * t)
    y = 200 + 200 * math.cos(6 * t)
    # Call native Win32 API function to change mouse position
    set_cursor_pos_func(int(x), int(y))

    if t - last_click > 0.3:
        # Every 0.3 seconds perform clicks

        last_click = t

        # To click I need to fill INPUT structure
        inp = INPUT()

        inp.type = INPUT_MOUSE
        inp.mi.dx = 0
        inp.mi.dy = 0
        inp.mi.mouseData = 0
        inp.mi.time = 0
        inp.mi.dwExtraInfo = None

        # Send mouse down input event
        inp.mi.dwFlags = MOUSEEVENTF_MOVE | MOUSEEVENTF_LEFTDOWN
        res = send_input_func(1, ctypes.pointer(inp), sizeof(INPUT))
        if res != 1:
            ctypes.FormatError(ctypes.GetLastError())

        # Send mouse up input event
        inp.mi.dwFlags = MOUSEEVENTF_MOVE | MOUSEEVENTF_LEFTUP
        res = send_input_func(1, ctypes.pointer(inp), sizeof(INPUT))
        if res != 1:
            ctypes.FormatError(ctypes.GetLastError())