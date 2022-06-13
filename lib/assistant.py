
import ctypes
from time import sleep
import win32api
import win32con
import pynput
import pyautogui

recoil_speed = 3

PUL = ctypes.POINTER(ctypes.c_ulong)

LEFT_ALT = 0x38
SendInput = ctypes.windll.user32.SendInput
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]


class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]


class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

# Actuals Functions
def PressKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def ReleaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008 | 0x0002, 0,
                        ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def auto_ping(enabled):
    if enabled:
        PressKey(LEFT_ALT)
        ReleaseKey(LEFT_ALT)
        PressKey(LEFT_ALT)
        ReleaseKey(LEFT_ALT)

# RECOIL
def activate_aim(is_aim, inpt_device, tx, ty, screenwidth, screenheight):
    if inpt_device == '1':
        m_left = win32api.GetKeyState(0x01)
        m_right = win32api.GetKeyState(0x02)

        if m_right < 0 and is_aim:
            # Move the mouse with these offsets
            #print(tx, ty)
            extra = ctypes.c_ulong(0)
            ii_ = pynput._util.win32.INPUT_union()
            ii_.mi = pynput._util.win32.MOUSEINPUT(tx, ty, 0, (0x0001 | 0x8000), 0, ctypes.cast(ctypes.pointer(extra), ctypes.c_void_p))
            command=pynput._util.win32.INPUT(ctypes.c_ulong(0), ii_)
            SendInput(1, ctypes.pointer(command), ctypes.sizeof(command))
            #win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE,
               # tx, ty, 0, 0)
    elif inpt_device == '2':
        # TODO CONTROLLER INPUT
            auto_ping()
    else:
        inpt_device = "1"
        print("Device set to Default 1 = Mouse")