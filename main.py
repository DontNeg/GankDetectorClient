import os
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
import sys

def processCaptureImg():
    w, h = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)
    ImageGrab.grab().crop((w / 1.15, 0, w, (h * h / 3000))).save("./snapshot.jpg")
    img = Image.open('./snapshot.jpg').convert('L')
    ret, img = cv2.threshold(np.array(img), 150, 255, cv2.THRESH_BINARY)
    img = Image.fromarray(img.astype(np.uint8))
    return img

def imgToText(img):
    text = re.sub(r'[^ \nA-Za-z/]+', '', pytesseract.image_to_string(img).replace(" ", "").lower())
    text = os.linesep.join([s for s in text.splitlines() if s])
    return text

def getClanList():
    header = {'authorization': f'{dotenv_values().get('TOKEN')}'}
    request = requests.get(f'https://discord.com/api/v9/channels/1234567891011121314/messages', headers=header)
    thing = json.loads(request.text)
    return thing

def getKnownGankers():
    clanlist = []
    for line in imgToText(processCaptureImg()).splitlines():
        for lineInside in getClanList()[0]['content'].splitlines():
            if SequenceMatcher(None, line, lineInside).ratio() > 0.65:
                clanlist.append(lineInside)
    clanlist = list(set(clanlist))
    os.remove("./snapshot.jpg")
    return clanlist

def main():
    if getattr(sys, 'frozen', False):
        _path = os.path.join(sys._MEIPASS, 'Tesseract-OCR/tesseract.exe')
        pytesseract.pytesseract.tesseract_cmd = _path
        ext_data_dir = sys._MEIPASS
    else:
        pytesseract.pytesseract.tesseract_cmd = r"C:/Tesseract-OCR/tesseract.exe"
        ext_data_dir = os.getcwd()
    load_dotenv(dotenv_path=os.path.join(ext_data_dir, '.env'))
    while True:
        timer = 0
        while True:
            time.sleep(0.1)
            timer+=0.1
            if keyboard.is_pressed(f'{dotenv_values().get('KEYBIND')}') or timer>=300:
                break
        clanlist = getKnownGankers()
        sys.stdout = StringIO()
        output_messages = ["No known gankers in your server", "Known gankers in your server"]
        output_message_index = 0 if len(clanlist)==0 else 1
        toast(f"{output_messages[output_message_index]} {clanlist}", duration='short', audio={'silent': 'true'})
        sys.stdout = sys.__stdout__
        print(f"{output_messages[output_message_index]} -", datetime.datetime.now().strftime("%H:%M:%S"))

if __name__ == "__main__":
    main()