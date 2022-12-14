import pyscreenshot as ss
import hashlib
import time
import json

from pynput import keyboard

# import subprocess

import win32api
import win32con

BOX = (1090, 680, 1788, 842)
bw, bh = (344, 76)
sl, st = (354, 86)

def click(x, y):
    win32api.SetCursorPos((x, y))
    # win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    # win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)


click(1090, 680)
exit(1)

FILE = 'bads.json'
with open(FILE, "r") as f:
    bads = json.load(f)


def my_write():
    start = time.time()
    s = ss.grab(bbox=BOX)
    lt = s.crop(box=(0, 0, bw, bh))
    rt = s.crop(box=(sl, 0, sl + bw, bh))
    lb = s.crop(box=(0, st, bw, st + bh))
    rb = s.crop(box=(sl, st, sl + bw, st + bh))

    hashes = []
    for im in [lt, rt, lb, rb]:
        print(im.getpixel((0, 0)))
        if (len(set(im.getpixel((0, 0))))) <= 1:
            hashes.append(hashlib.sha1(im.tobytes()).hexdigest())
    hashes.sort()

    if hashes not in bads:
        bads.append(hashes)
        with open(FILE, "w") as f:
            json.dump(bads, f)
        print("saved")

    for h in bads:
        print("> ", set({'be2df90210d335487dd56eab8ab2c4f11f67585e',
                         '85fa5c89746f2780c77562f1e81294adc200ffc5',
                         '5c76e325e8932b72ec6f78b96b186d8387712145',
                         '58a0c0672baecaf22d3b1b2b4eded2df9b811f57'}).difference(set(h)))
    print(bads)

    # s.save('test.png')
    # lt.save('lt.png')
    # rt.save('rt.png')
    # lb.save('lb.png')
    # rb.save('rb.png')
    print(time.time() - start)


pressed = set()

COMBINATIONS = [
    {
        "keys": [
            {keyboard.Key.cmd, keyboard.KeyCode(char="w")},
            {keyboard.Key.cmd, keyboard.KeyCode(char="W")},
        ],
        "command": my_write,
    },
]


# def run(s):
#     subprocess.Popen(s)

def on_press(key):
    pressed.add(key)
    print(pressed)
    for c in COMBINATIONS:
        for keys in c["keys"]:
            if keys.issubset(pressed):
                c["command"]()


def on_release(key):
    if key in pressed:
        pressed.remove(key)


with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
