import ctypes

EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible
SetForeground = ctypes.windll.user32.SetForegroundWindow
GetForegroundWindow = ctypes.windll.user32.GetForegroundWindow

titles = []
hwnds = []


def foreach_window(hwnd, lParam):
    if IsWindowVisible(hwnd):
        length = GetWindowTextLength(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        GetWindowText(hwnd, buff, length + 1)
        titles.append(buff.value)
        hwnds.append(hwnd)

    return True

EnumWindows(EnumWindowsProc(foreach_window), 0)

print(titles)

print(GetForegroundWindow())

# SetForeground(hwnds[3])
