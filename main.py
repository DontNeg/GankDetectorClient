import os
import sys
from io import StringIO
import datetime
from PIL import Image, ImageGrab
import pytesseract
import re
import cv2
import numpy as np
import ctypes
import json
from difflib import SequenceMatcher
from win11toast import toast
from dotenv import load_dotenv, dotenv_values
import time
import keyboard
import requests

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()
timer = 0
extDataDir = os.getcwd()
if getattr(sys, 'frozen', False):
    extDataDir = sys._MEIPASS
load_dotenv(dotenv_path=os.path.join(extDataDir, '.env'))
while True:
    while True:
        time.sleep(0.1)
        timer+=0.1
        if keyboard.is_pressed(f'{dotenv_values().get('KEYBIND')}'):
            break
        if timer>=300:
            timer=0
            break
    w, h = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)
    ImageGrab.grab().crop((w / 1.15, 0, w, (h * h / 3000))).save("./snapshot.jpg")
    img = Image.open('./snapshot.jpg').convert('L')
    ret, img = cv2.threshold(np.array(img), 150, 255, cv2.THRESH_BINARY)
    img = Image.fromarray(img.astype(np.uint8))
    text = re.sub(r'[^ \nA-Za-z/]+', '', pytesseract.image_to_string(img).replace(" ", "").lower())
    text = os.linesep.join([s for s in text.splitlines() if s])
    os.remove("./snapshot.jpg")
    header = {'authorization': ''}
    request = requests.get(f'https://discord.com/api/v9/channels/1288958532099506186/messages', headers=header)
    thing = json.loads(request.text)
    clanlist = []
    for line in text.splitlines():
        for lineInside in thing[0]['content'].splitlines():
            if similar(line, lineInside)>0.65:
                clanlist.append(lineInside)
    clanlist = list(set(clanlist))
    if len(clanlist)==0:
        sys.stdout = StringIO()
        toast("No known gankers in your server", duration='short', audio={'silent': 'true'})
        sys.stdout = sys.__stdout__
        print("No known gankers in your server -", datetime.datetime.now().strftime("%H:%M:%S"))
    elif len(clanlist) > 0:
        sys.stdout = StringIO()
        toast(f"Known gankers in your server {clanlist}", duration='short', audio={'silent': 'true'})
        sys.stdout = sys.__stdout__
        print("Known gankers in your server -", datetime.datetime.now().strftime("%H:%M:%S"))