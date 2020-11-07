import win32gui
import win32con
import pyautogui

toplist = []
winlist = []

width, height= pyautogui.size()


def enum_callback(hwnd, results):
    winlist.append((hwnd, win32gui.GetWindowText(hwnd)))

win32gui.EnumWindows(enum_callback, toplist)

grid3 = [(hwnd, title) for hwnd, title in winlist if title.startswith('Grid 3')]
print(winlist)
print(grid3)
# just grab the first window that matches
grid3 = grid3[0]
(left, top, right, bottom) = win32gui.GetWindowRect(grid3[0])
print(left, top, right, bottom)
#win32gui.SetForegroundWindow(grid3[0])
#win32gui.ShowWindow(grid3[0], win32con.SW_MAXIMIZE)
win32gui.MoveWindow(grid3[0], 0, 0, width,height, False)