from collections import defaultdict

import pyscreenshot as ss
import hashlib
import json
# from PIL import Image

from pynput import keyboard
from threading import Thread

# import subprocess

import win32api
import win32con

EXTRA_H = 100
BOX = (1090, 680 - EXTRA_H, 1788, 842)
# BOX = (1090, 684, 1788, 846)
bw, bh = 344, 76
sl, st = 354, 86

FILE = 'bad2.json'


# s = Image.open('last.png')
# lt = s.crop(box=(0, 0, bw, bh))
# rt = s.crop(box=(sl, 0, sl + bw, bh))
# lb = s.crop(box=(0, st, bw, st + bh))
# rb = s.crop(box=(sl, st, sl + bw, st + bh))
#
# hashes = []
# for im in [lt, rt, lb, rb]:
#     p = im.getpixel((0, 0))
#     print(p)
#     if p[1] < 200:
#         hashes.append(hashlib.sha1(im.tobytes()).hexdigest())
# print(sorted(hashes))
#
# exit(1)

def click(x, y):
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)


def m_get_hashes():
    s = ss.grab(bbox=BOX)
    lt = s.crop(box=(0, EXTRA_H, bw, EXTRA_H + bh))
    rt = s.crop(box=(sl, EXTRA_H, sl + bw, EXTRA_H + bh))
    lb = s.crop(box=(0, EXTRA_H + st, bw, EXTRA_H + st + bh))
    rb = s.crop(box=(sl, EXTRA_H + st, sl + bw, EXTRA_H + st + bh))
    ex = s.crop(box=(0, 0, sl + bw, EXTRA_H))

    # s.save('s.png')
    # lt.save('lt.png')
    # rt.save('rt.png')
    # lb.save('lb.png')
    # rb.save('rb.png')
    # ex.save('ex.png')
    hashes = []
    all_hashes = []
    for im in [lt, rt, lb, rb]:
        p = im.getpixel((0, 0))
        h = hashlib.sha1(im.tobytes()).hexdigest()
        all_hashes.append(h)

        if p[1] < 200:
            hashes.append(h)
    # s.save('tmp/' + '_'.join(all_hashes) + '.png')
    return sorted(hashes), all_hashes, hashlib.sha1(ex.tobytes()).hexdigest()


def m_search():
    hashes, all, ex = m_get_hashes()
    if len(hashes) != 4:
        print(f'search {len(hashes)}')
        return

    if ex in bads:
        for h in bads[ex]:
            t = set(hashes).difference(set(h))
            if len(t) == 1:
                print(f"found {t}, {hashes}")
                if all[0] in t:
                    print('lt')
                    click(BOX[0] + bw // 2, EXTRA_H + BOX[1] + bh // 2)
                if all[1] in t:
                    print('rt')
                    click(BOX[0] + sl + bw // 2, EXTRA_H + BOX[1] + bh // 2)
                if all[2] in t:
                    print('lb')
                    click(BOX[0] + bw // 2, EXTRA_H + BOX[1] + st + bh // 2)
                if all[3] in t:
                    print('rb')
                    click(BOX[0] + sl + bw // 2, EXTRA_H + BOX[1] + st + bh // 2)
                return

    print(f"not found", all)
    win32api.SetCursorPos((int((BOX[0] + BOX[2]) / 2), int((BOX[1] + BOX[3]) / 2)))


def m_write():
    hashes, _, ex = m_get_hashes()
    if len(hashes) != 3:
        print(f'save {len(hashes)}')
        return

    if ex not in bads:
        bads[ex] = []

    if hashes not in bads[ex]:
        bads[ex].append(hashes)
        with open(FILE, "w") as file:
            json.dump(bads, file)
        print("saved", len(bads))
    else:
        print("exist")


try:
    with open(FILE, "r") as f:
        bads = json.load(f)
except FileNotFoundError:
    bads = defaultdict(list)

pressed = set()

COMBINATIONS = [
    {
        "keys": [
            {keyboard.Key.cmd, keyboard.KeyCode(char="A")},
            {keyboard.Key.cmd, keyboard.KeyCode(char="a")},
            {keyboard.Key.cmd, keyboard.KeyCode(char="Ф")},
            {keyboard.Key.cmd, keyboard.KeyCode(char="ф")},
        ],
        "command": m_search,
    },
    {
        "keys": [
            {keyboard.Key.cmd, keyboard.KeyCode(char="S")},
            {keyboard.Key.cmd, keyboard.KeyCode(char="s")},
            {keyboard.Key.cmd, keyboard.KeyCode(char="Ы")},
            {keyboard.Key.cmd, keyboard.KeyCode(char="ы")},
        ],
        "command": m_write,
    },
]


# def run(s):
#     subprocess.Popen(s)

def on_press(key):
    if key in pressed: return

    pressed.add(key)
    for c in COMBINATIONS:
        for keys in c["keys"]:
            if keys.issubset(pressed):
                Thread(target=c["command"]).start()


def on_release(key):
    if key in pressed:
        pressed.remove(key)


with keyboard.Listener(on_press=on_press, on_release=on_release, suppress=True) as listener:
    listener.join()
