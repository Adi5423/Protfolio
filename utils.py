# utils.py
import os

IS_SERVER = os.getenv('ENVIRONMENT') == 'production'

try:
    import pyttsx3
    SPEECH_AVAILABLE = True
except:
    SPEECH_AVAILABLE = False

try:
    import screen_brightness_control as sbc
    BRIGHTNESS_CONTROL_AVAILABLE = True
except:
    BRIGHTNESS_CONTROL_AVAILABLE = False

def speak(text):
    if SPEECH_AVAILABLE and not IS_SERVER:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    else:
        print(f"Would speak: {text}")

def set_brightness(level):
    if BRIGHTNESS_CONTROL_AVAILABLE and not IS_SERVER:
        sbc.set_brightness(level)
    else:
        print(f"Would set brightness to: {level}")