# 1. First declare all global variables at the top
TURBO = False
use_voice_input = True
# Global conversation history
conversation_history = []

# 2. Import statements
import webbrowser
import time
import os
import sys
import speech_recognition as sr
# import pyautogui
import wikipedia
import io
import pywhatkit
import psutil
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import screen_brightness_control as sbc
from datetime import datetime
import json
import threading
import requests
import pyttsx3 as ptx3
from groq import Groq
import subprocess
# import pyautogui
import random

# 3. Constants and configurations
GROQ_API = "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"
client = Groq(api_key=GROQ_API)
models = ["gemma-7b-it", "mixtral-8x7b-32768"]

# 4. Initialize components
engine = ptx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
recognizer = sr.Recognizer()

# 5. Other global variables
home_directory = os.path.expanduser("~")
desktop_location = os.path.join(home_directory, "Desktop")
city_name = "Lucknow"
API_K = 'ed4cc0502e9e415825ea58832a79f3f3'
query = ""
file_name = "example.txt"
file_content = "This is an example text file.\nIt contains multiple lines.\nHello, World!"
sensitivity = 2
sensitivity_thresholds = {
    1: 10, 2: 20, 3: 30, 4: 40, 5: 50, 6: 60, 7: 70
}

# 6. Initialize audio devices
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# 7. Keywords list
keying = ["wikipedia", "time now", "date now", "current date and time", "who is", 
            "open youtube", "open google", "search", "open notepad", "play", 
            "create folder", "what weather current", "how weather current", "scroll",
            "create file", "set reminder", "check reminders", "show reminders", 
            "delete reminder", "remove reminder", "increase volume", "decrease volume",
            "increase brightness", "decrease brightness", "cpu usage", "battery status",
            "turn on airplane mode", "turn off wifi", "quit", "exit", "goodbye"]

# 8. Your functions (GenerateGroq, speakPTX, etc.)
def GenerateGroq(message):
    # Personality traits and system message
    personality_traits = """
    - Show enthusiasm and positivity
    - Use casual language, slang, and fillers
    - Be expressive with emojis
    - Use natural speech patterns
    - Include occasional filler words
    - Use informal expressions and contractions
    """
    
    casual_expressions = [
        "y'know", "like", "basically", "literally", "totally",
        "umm", "uh", "hmm", "ah", "oh", "oops",
        "gonna", "wanna", "gotta", "ain't",
        "tbh", "ngl", "fr", "idk"
    ]

    emoji_map = {
        'happy': ['😊', '😄', '🥰', '😁', '✨'],
        'sad': ['😔', '🥺', '😢', '💔'],
        'surprise': ['😮', '😲', '🤯'],
        'thinking': ['🤔', '💭'],
        'agreement': ['👍', '💯'],
        'funny': ['😂', '🤣'],
        'generic': ['💁‍♀️', '✨']
    }

    system_message = f"""You are Aistie, a friendly AI assistant that speaks casually like a human:
    {personality_traits}
    Mix in casual expressions and emojis naturally but don't overdo it.
    Use contractions and informal language."""

    # Get response from Gro q
    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[
            {"role": "system", "content": system_message},
        ] + conversation_history + [
            {"role": "user", "content": message}
        ],
        temperature=0.7,
        max_tokens=50,  # Limit response length to keep it short
        presence_penalty=0.6,
        frequency_penalty=0.6
    )

    raw_response = response.choices[0].message.content.strip()

    # Add random filler (20% chance)
    if random.random() < 0.2:
        filler = random.choice(casual_expressions)
        raw_response = f"{filler}, {raw_response}"

    # Emoji and slang modifications based on content
    if any(word in raw_response.lower() for word in ['happy', 'glad', 'great']):
        raw_response += f" {' '.join(random.sample(emoji_map['happy'], 1))}"
    elif any(word in raw_response.lower() for word in ['sad', 'sorry']):
        raw_response += f" {' '.join(random.sample(emoji_map['sad'], 1))}"
    elif any(word in raw_response.lower() for word in ['wow', 'amazing']):
        raw_response += f" {' '.join(random.sample(emoji_map['surprise'], 1))}"

    # Special greeting handling
    if "hello" in message.lower() or "hi" in message.lower():
        raw_response = f"Hey! {raw_response} 👋 {random.choice(emoji_map['happy'])}"
    elif "bye" in message.lower():
        raw_response = f"Catch ya later! ✌️ {random.choice(emoji_map['happy'])}"

    # Add random trailing expressions (10% chance)
    if random.random() < 0.1:
        raw_response += f" {random.choice(['lol', 'fr', 'ngl'])} {random.choice(emoji_map['funny'])}"

    return raw_response

def speakPTX(text, is_text_mode):
    if is_text_mode:
        print("Assistant:", text)
    else:
        engine.say(text)
        engine.runAndWait()

def speakPTXinput(text, is_text_mode):
    if is_text_mode:
        print("Assistant:", text)
        return input("You: ").lower()
    else:
        engine.say(text)
        engine.runAndWait()
        queue = takeCommand()
        return queue.lower()

def get_drive_names():
    try:
        # Run the command and capture the output
        result = subprocess.run(['wmic', 'logicaldisk', 'get', 'name'], capture_output=True, text=True, check=True)
        
        # Split the output into lines and filter out empty lines
        drive_names = [line.strip() for line in result.stdout.splitlines() if line.strip()]

        # Remove the header if present
        if drive_names and drive_names[0] == "Name":
            drive_names.pop(0)

        return drive_names

    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
        return []
    
def get_weather(city_name, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        weather_description = data['weather'][0]['description']
        temperature = round(data['main']['temp'])
        feels_like = round(data['main']['feels_like'])
        humidity = data['main']['humidity']

        return {
            'description': weather_description,
            'temperature': temperature,
            'feels_like': feels_like,
            'humidity': humidity
        }
    else:
        print("Error:", response.status_code)
        return None  # Return None if there's an error

# def continuous_scroll(amount):
#     global scrolling
#     while scrolling:  # Run while scrolling is True
#         pyautogui.scroll(amount)
#         time.sleep(0.5)  # Adjust the sleep duration as needed

# def listen_for_stop_command(is_text_mode):
#     global scrolling
#     while True:
#         command = takeCommand(is_text_mode)
#         if "stop" in command:
#             print("Stopping scrolling.")
#             scrolling = False  # Set scrolling to False to stop scrolling
#             speakPTX("Sure", is_text_mode)
#             return  # Exit the loop to stop scrolling

# def handle_scroll_command(is_text_mode):
#     global scrolling
#     speakPTX("Would you like to scroll upward or downward?", is_text_mode)
#     direction = takeCommand(is_text_mode)
    
#     if "upward" in direction:
#         amount = 100  # Positive value for up
#     elif "downward" in direction:
#         amount = -100  # Negative value for down
#     else:
#         speakPTX("I didn't understand that. Please say or type 'upward' or 'downward'.", is_text_mode)
#         return

#     speakPTX(f"You have 3 seconds to open the app. {'Type' if is_text_mode else 'Say'} stop to stop. Starting in...", is_text_mode)
#     for i in range(3, 0, -1):
#         speakPTX(str(i), is_text_mode)  # Countdown
#         time.sleep(1)

#     scrolling = True  # Start scrolling
#     listener_thread = threading.Thread(target=listen_for_stop_command, args=(is_text_mode,))
#     listener_thread.start()
    
#     # Start continuous scrolling
#     continuous_scroll(amount)
#     listener_thread.join()  # Wait for the listener thread to finish
    
'''
def speakTTS(text):
    tts = gTTS(text=text, lang='en', slow=False)
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    mixer.music.load(mp3_fp)
    mixer.music.play()
    while mixer.music.get_busy():
        pygame.time.Clock().tick(10)
'''
        
def takeCommand(is_text_mode):
    if is_text_mode:
        query = input("You: ").lower()
        print(f"User typed: {query}\n")
        if "quit" in query or "exit" in query or ("good" in query and "bye" in query):
            print("Exiting...")
            print("Nice with you buddy, Stay Connected.")
            # sys.exit()
        return query
    else:
        # Original voice recognition code
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.pause_threshold = 1
            audio = recognizer.listen(source)
        try:
            print("Recognizing...")
            query = recognizer.recognize_google(audio, language='en-in')
            print(f"User said: {query}\n")
            if "quit" in query or "exit" in query or ("good" in query and "bye" in query):
                print("Exiting...")
                speakPTX("Nice with you buddy, Stay Connected.")
                # sys.exit()
            return query.lower()
        except Exception as e:
            print("Say that again please...")
            return "None"

def open_notepad():
    os.system("notepad.exe")
    time.sleep(1)

def create_folder(folder_path):
    os.makedirs(folder_path, exist_ok=True)
    print(f"Folder created or already exists at: {folder_path}")

def create_file(file_path, content):
    with open(file_path, 'w') as file:
        file.write(content)
    print(f"File created successfully at: {file_path}")

def takeCommandNotes(is_text_mode):
    if is_text_mode:
        print("Type your notes (type 'stop' to end):")
        notes = []
        while True:
            line = input()
            if line.lower() == 'stop':
                break
            notes.append(line)
        return ' '.join(notes)
    else:
        query = ""  # Initialize an empty string to hold the commands
        with sr.Microphone() as source:
            print("Listening... (Say 'stop' to end)")
            recognizer.pause_threshold = 1
            
            while True:
                try:
                    audio = recognizer.listen(source, timeout=5)
                    print("Recognizing...")
                    command = recognizer.recognize_google(audio, language='en-in')
                    print(f"User said: {command}\n")
                    
                    if "stop" in command.lower():
                        break
                    
                    query += command + " "
                    
                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    print("Say that again please...")
                    continue

        return query.strip()

def Notepad(is_text_mode):
    speakPTX("Tell Me The Query.", is_text_mode)
    speakPTX("I Am Ready To Write.", is_text_mode)

    writes = takeCommandNotes(is_text_mode)

    time = datetime.now().strftime("%H:%M")
    filename = str(time).replace(":","-") + "-note.txt"

    with open(filename,"w") as file:
        file.write(writes)

    path_1 = ".\\" + str(filename)
    path_2 = ".\\" + str(filename)

    os.rename(path_1,path_2)
    os.startfile(path_2)

def set_reminder(is_text_mode):
    speakPTX("Sure, I can help you set a reminder. What should I call this reminder?", is_text_mode)
    reminder_key = takeCommand(is_text_mode)
    speakPTX("What would you like me to remind you about?", is_text_mode)
    reminder_text = takeCommand(is_text_mode)
    
    try:
        with open('reminders.json', 'r') as f:
            reminders = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        reminders = {}
    reminders[reminder_key] = reminder_text
    try:
        with open('reminders.json', 'w') as f:
            json.dump(reminders, f, indent=4)
        speakPTX(f"Reminder '{reminder_key}' has been set.", is_text_mode)
    except Exception as e:
        speakPTX(f"I'm sorry, I encountered an error while saving the reminder. The error was: {str(e)}", is_text_mode)

def check_reminders(is_text_mode):
    try:
        with open('reminders.json', 'r') as f:
            reminders = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        speakPTX("No reminders found.", is_text_mode)
        return

    if reminders:
        speakPTX("Here are your current reminders:", is_text_mode)
        for key, reminder in reminders.items():
            speakPTX(f"{key}: {reminder}", is_text_mode)
    else:
        speakPTX("You have no reminders set.", is_text_mode)

def delete_reminder(reminder_key, is_text_mode):
    try:
        with open('reminders.json', 'r') as f:
            reminders = json.load(f)
        if reminder_key in reminders:
            del reminders[reminder_key]
            with open('reminders.json', 'w') as f:
                json.dump(reminders, f, indent=4)
            speakPTX(f"Reminder '{reminder_key}' has been deleted.", is_text_mode)
        else:
            speakPTX(f"No reminder found with the key '{reminder_key}'.", is_text_mode)
    except FileNotFoundError:
        speakPTX("No reminders file found.", is_text_mode)
    except json.JSONDecodeError:
        speakPTX("The reminders file is empty or corrupted.", is_text_mode)

def CreationFolder(query, is_text_mode):
    if ("create" in query or "make" in query or "generate" in query) and "folder" in query:
        speakPTX(f"Sure, I have permissions for {len(drives)} drives and your desktop to create a folder.", is_text_mode)

        if len(drives) > 0:
            speakPTX("The available drives are:", is_text_mode)
            for drive in drives:
                speakPTX(drive + " drive", is_text_mode)
                print(drive, "drive")
        else:
            speakPTX("No drives available.", is_text_mode)

        speakPTX("Where would you like to create the folder? You can say the drive name or 'desktop'.", is_text_mode)
        InQuery = takeCommand(is_text_mode).lower()
        print(f"User {'typed' if is_text_mode else 'said'}: {InQuery}")

        # Check if the user wants to create the folder on the desktop
        if "desktop" in InQuery:
            speakPTX("What would you like to name the folder?", is_text_mode)
            FolderName = takeCommand(is_text_mode)
            folderPath = os.path.join(InQuery + "\\\\", FolderName)  # Construct the path
            try:
                os.makedirs(folderPath, exist_ok=True)  # Create the folder
                speakPTX(f"Folder created on the desktop at {folderPath}.", is_text_mode)
            except Exception as e:
                speakPTX(f"Failed to create folder on the desktop. Error: {str(e)}", is_text_mode)

        # Check if the user wants to create the folder in one of the drives
        elif InQuery in drives:
            InQuery = InQuery.replace("drive","")
            speakPTX("What would you like to name the folder?", is_text_mode)
            FolderName = takeCommand(is_text_mode)
            folderPath = os.path.join(InQuery + "\\\\", FolderName)  # Construct the path
            try:
                os.makedirs(folderPath, exist_ok=True)  # Create the folder
                speakPTX(f"Folder created in {InQuery.upper()} drive at {folderPath}.", is_text_mode)
            except Exception as e:
                speakPTX(f"Failed to create folder in {InQuery.upper()} drive. Error: {str(e)}", is_text_mode)

        else:
            speakPTX("I didn't understand where you want to create the folder. Please specify a valid drive or 'desktop'.", is_text_mode)

def wishMe(is_text_mode):
    hour = datetime.now().hour
    if hour < 12:
        speakPTX("Good morning!", is_text_mode)
    elif hour < 18:
        speakPTX("Good afternoon!", is_text_mode)
    else:
        speakPTX("Good evening!", is_text_mode)
    speakPTX("I am your personal assistant, Aistie. How may I assist you today?", is_text_mode)

drives = get_drive_names()

def process_single_message(message, is_text_mode=True):
        global TURBO
        message = message.lower()
        if message == "none":
            pass
        else:
            try:
                # The rest of your existing code remains unchanged
                if "wikipedia" in message:
                    # return ("Searching Wikipedia...")
                    message = message.replace("wikipedia", "")
                    results = wikipedia.summary(message, sentences=2)
                    return (("According to Wikipedia, " + results))

                elif "time now" in message:
                    current_time = datetime.now().strftime("%H:%M")
                    return (f"The current time is {current_time}")

                elif "date now" in message:
                    current_date = datetime.now().strftime("%Y-%m-%d")
                    return (f"The current date is {current_date}")

                elif "current date and time" in message:
                    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M")
                    return (f"The current date and time is {current_datetime}")

                elif "who is" in message:
                    person = message.replace("who is", "").strip()
                    try:
                        info = wikipedia.summary(person, sentences=2)
                        return (f"According to Wikipedia, {info}")
                    except wikipedia.exceptions.DisambiguationError:
                        return (f"There are multiple results for {person}. Please be more specific.")
                    except wikipedia.exceptions.PageError:
                        return (f"I couldn't find any information about {person}")

                # # searching for files
                # elif "find" in message:
                #     message = message.replace("find", "")
                #     namesearch=speakPTXinput("Sure . say only the file name please")
                #     searchmessage = speakPTXinput("Sure  , for text file say keyword the text , and image as png jpg or it's extension name only , same for videos. ")
                #     if "the" in searchmessage and "text" in searchmessage:
                #         # return ("Searching for text files...")
                #         global typeExten
                #         typeExten=f"{namesearch}.txt"
                #     # Press the Windows key
                #     pyautogui.press('win')
                #     # Give the Start menu a moment to open
                #     time.sleep(1.5)
                #     # Type the search message
                #     pyautogui.typewrite(f'Documents: {typeExten}', interval=0.1)
                #     time.sleep(1.5+.5)
                #     Newmessage=speakPTXinput("Sure  i founnd these results. i can open the first one, or tell the number count to open, if many files")
                #     checkResponse=GenerateGroq(f" \" {Newmessage} \" just return the number this message if no number is there return false , if numbers are there just return the numbers in integer only. No extra data should be included in the response either False or any number if there.")
                #     if checkResponse is not False:
                #         for i in range(15):
                #             if str(i) == str(checkResponse):
                #                 for _ in range(int(i)):
                #                     pyautogui.press('down')
                #                     time.sleep(.9)  
                #         pyautogui.press('enter')  
                #     else:
                #         return ("Okay Sure ")
                    
                elif "open youtube" in message:
                    webbrowser.open_new("https://youtube.com")
                    return ("Opening YouTube")

                elif "write" in message and "notepad" in message:
                    Notepad()
                
                elif "copied" in message or "copy" in message:
                    return ("Sure  please you want to copy something or paste something ? Or should i save your copied text to dot txt file.")

                elif "open google" in message:
                    webbrowser.open_new("https://google.com")
                    return ("Opening Google")

                elif "search" in message:
                    search_message = message.replace("search", "").strip()
                    webbrowser.open_new_tab(f"https://www.google.com/search?q={search_message}")
                    return (f"Here are the search results for {search_message}")

                elif "open notepad" in message:
                    open_notepad()
                    return ("Opening Notepad")
                
                elif "hey"in message:
                    return(GenerateGroq(message))

                elif "play" in message:
                    song = message.replace("play", "").strip()
                    pywhatkit.playonyt(song)
                    return (f"Playing {song} on YouTube")

                elif ("create" in message or "make" in message or "generate" in message) and "folder" in message:
                    CreationFolder(message)

                elif ("weather" in message) and ("what" in message or "how" in message):
                    weather_data = get_weather(city_name, API_K)
                    if weather_data:
                        weather_info = f"Sure , the weather is {weather_data['description']} with temperature {weather_data['temperature']}°C, and humidity of {weather_data['humidity']}%, feels like nearly {weather_data['feels_like']}°C."
                        print(weather_info)
                        return (weather_info)

                elif "create file" in message:
                    folder_path = os.path.join(os.getcwd(), "new_folder")
                    file_path = os.path.join(folder_path, file_name)
                    create_file(file_path, file_content)
                    return (f"File created at {file_path}")

                elif "set reminder" in message or "set a reminder" in message:
                    set_reminder()

                elif "check reminders" in message or "show reminders" in message:
                    check_reminders()

                elif "delete reminder" in message or "remove reminder" in message:
                    return ("Which reminder would you like to delete?")
                    reminder_key = takeCommand()
                    delete_reminder(reminder_key)

                elif "increase volume" in message:
                    current_volume = volume.GetMasterVolumeLevelScalar()
                    new_volume = min(1.0, current_volume + 0.1)
                    volume.SetMasterVolumeLevelScalar(new_volume, None)
                    return (f"Increased volume to {int(new_volume * 100)}%")

                elif "decrease volume" in message:
                    current_volume = volume.GetMasterVolumeLevelScalar()
                    new_volume = max(0.0, current_volume - 0.1)
                    volume.SetMasterVolumeLevelScalar(new_volume, None)
                    return (f"Decreased volume to {int(new_volume * 100)}%")

                elif "increase brightness" in message:
                    current_brightness = sbc.get_brightness()[0]
                    new_brightness = min(100, current_brightness + 10)
                    sbc.set_brightness(new_brightness)
                    return (f"Increased brightness to {new_brightness}%")

                elif "decrease brightness" in message:
                    current_brightness = sbc.get_brightness()[0]
                    new_brightness = max(0, current_brightness - 10)
                    sbc.set_brightness(new_brightness)
                    return (f"Decreased brightness to {new_brightness}%")

                elif "cpu usage" in message:
                    cpu_usage = psutil.cpu_percent(interval=1)
                    return (f"The current CPU usage is {cpu_usage}%")

                elif "battery status" in message:
                    battery = psutil.sensors_battery()
                    if battery:
                        percent = battery.percent
                        is_plugged = battery.power_plugged
                        status = "plugged in" if is_plugged else "not plugged in"
                        return (f"The battery is at {percent}% and is {status}.")
                    else:
                        return ("Unable to retrieve battery status.")

                elif "turn on airplane mode" in message:
                    os.system("start ms-settings:network-airplanemode")
                    return ("Opening Airplane mode settings.")

                elif "turn off wifi" in message:
                    os.system("netsh wlan set hostednetwork mode=disallow")
                    return ("Wi-Fi has been turned off.")

                elif "quit" in message or "exit" in message or "goodbye" in message:
                    print("Exiting...")
                    return ("NIce with you buddy,Stay Connected.")
                    # sys.exit()

                elif "switch to text input" in message:
                    use_voice_input = False
                    return ("Switched to text input mode. You can now type your commands.")

                elif "switch to voice input" in message:
                    use_voice_input = True
                    return ("Switched to voice input mode. Listening for your commands.")
                
                elif ("turn"in message and "on" in message and "turbo" in message) or ("activate"in message and "turbo"in message)or ("turbo"in message and ("on"in message or "activate" in message or  "start" in message or "enable" in message)):
                    TURBO=True
                    return  ("Turbo mode activated. The responses from now will be AI Linked")
                
                else:
                    # AI message generation by the Groq API
                    if TURBO:
                        try:
                            response = GenerateGroq(message)
                            # print(response)
                            return (response)
                        except Exception as e:
                            print(e)
                            return ("Sure  you may check your API or the Internet Connection first for Turbo Mode features.")
                    else:
                        return("Conversational responses need Turbo Mode Activation. \n *AI Linked responses*")

                        if ("turn" in AImessage and "on" in AImessage) or "yes" in AImessage or "activate" in AImessage and "turbo" in AImessage:
                            TURBO = True
                            response = GenerateGroq(message)
                            # print(response)
                            return (response)
            except Exception as e:
                print(e)

def main(is_text_mode):
    global TURBO
    while True:
        query = takeCommand(is_text_mode)
        query = query.lower()
        if query == "none":
            continue
        else:
            try:
                # The rest of your existing code remains unchanged
                if "wikipedia" in query:
                    speakPTX("Searching Wikipedia...")
                    query = query.replace("wikipedia", "")
                    results = wikipedia.summary(query, sentences=2)
                    speakPTX(("According to Wikipedia, " + results),is_text_mode)

                elif "time now" in query:
                    current_time = datetime.now().strftime("%H:%M")
                    speakPTX(f"The current time is {current_time}",is_text_mode)

                elif "date now" in query:
                    current_date = datetime.now().strftime("%Y-%m-%d")
                    speakPTX(f"The current date is {current_date}",is_text_mode)

                elif "current date and time" in query:
                    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M")
                    speakPTX(f"The current date and time is {current_datetime}",is_text_mode)

                elif "who is" in query:
                    person = query.replace("who is", "").strip()
                    try:
                        info = wikipedia.summary(person, sentences=2)
                        speakPTX(f"According to Wikipedia, {info}",is_text_mode)
                    except wikipedia.exceptions.DisambiguationError:
                        speakPTX(f"There are multiple results for {person}. Please be more specific.",is_text_mode)
                    except wikipedia.exceptions.PageError:
                        speakPTX(f"I couldn't find any information about {person}",is_text_mode)

                # # searching for files
                # elif "find" in query:
                #     query = query.replace("find", "")
                #     namesearch=speakPTXinput("Sure . say only the file name please",is_text_mode)
                #     searchquery = speakPTXinput("Sure  , for text file say keyword the text , and image as png jpg or it's extension name only , same for videos. ",is_text_mode)
                #     if "the" in searchquery and "text" in searchquery:
                #         speakPTX("Searching for text files...",is_text_mode)
                #         global typeExten
                #         typeExten=f"{namesearch}.txt"
                #     # Press the Windows key
                #     pyautogui.press('win')
                #     # Give the Start menu a moment to open
                #     time.sleep(1.5)
                #     # Type the search query
                #     pyautogui.typewrite(f'Documents: {typeExten}', interval=0.1)
                #     time.sleep(1.5+.5)
                #     NewQuery=speakPTXinput("Sure  i founnd these results. i can open the first one, or tell the number count to open, if many files",is_text_mode)
                #     checkResponse=GenerateGroq(f" \" {NewQuery} \" just return the number this query if no number is there return false , if numbers are there just return the numbers in integer only. No extra data should be included in the response either False or any number if there.")
                #     if checkResponse is not False:
                #         for i in range(15):
                #             if str(i) == str(checkResponse):
                #                 for _ in range(int(i)):
                #                     pyautogui.press('down')
                #                     time.sleep(.9)  
                #         pyautogui.press('enter')  
                #     else:
                #         speakPTX("Okay Sure ")
                    
                elif "open youtube" in query:
                    webbrowser.open_new("https://youtube.com")
                    speakPTX("Opening YouTube",is_text_mode)

                elif "write" in query and "notepad" in query:
                    Notepad(is_text_mode)
                
                elif "copied" in query or "copy" in query:
                    speakPTX("Sure  please you want to copy something or paste something ? Or should i save your copied text to dot txt file.",is_text_mode)

                elif "open google" in query:
                    webbrowser.open_new("https://google.com")
                    speakPTX("Opening Google",is_text_mode)

                elif "search" in query:
                    search_query = query.replace("search", "").strip()
                    webbrowser.open_new_tab(f"https://www.google.com/search?q={search_query}")
                    speakPTX(f"Here are the search results for {search_query}",is_text_mode)

                elif "open notepad" in query:
                    open_notepad()
                    speakPTX("Opening Notepad",is_text_mode)

                elif "play" in query:
                    song = query.replace("play", "").strip()
                    speakPTX(f"Playing {song} on YouTube",is_text_mode)
                    pywhatkit.playonyt(song)

                elif ("create" in query or "make" in query or "generate" in query) and "folder" in query:
                    CreationFolder(query,is_text_mode)

                elif ("weather" in query) and ("what" in query or "how" in query):
                    weather_data = get_weather(city_name, API_K)
                    if weather_data:
                        weather_info = f"Sure , the weather is {weather_data['description']} with temperature {weather_data['temperature']}°C, and humidity of {weather_data['humidity']}%, feels like nearly {weather_data['feels_like']}°C."
                        print(weather_info)
                        speakPTX(weather_info,is_text_mode)

                elif "create file" in query:
                    folder_path = os.path.join(os.getcwd(), "new_folder")
                    file_path = os.path.join(folder_path, file_name)
                    create_file(file_path, file_content)
                    speakPTX(f"File created at {file_path}",is_text_mode)

                elif "set reminder" in query or "set a reminder" in query:
                    set_reminder(is_text_mode)

                elif "check reminders" in query or "show reminders" in query:
                    check_reminders(is_text_mode)

                elif "delete reminder" in query or "remove reminder" in query:
                    speakPTX("Which reminder would you like to delete?",is_text_mode)
                    reminder_key = takeCommand(is_text_mode)
                    delete_reminder(reminder_key,is_text_mode)

                elif "increase volume" in query:
                    current_volume = volume.GetMasterVolumeLevelScalar()
                    new_volume = min(1.0, current_volume + 0.1)
                    volume.SetMasterVolumeLevelScalar(new_volume, None)
                    speakPTX(f"Increased volume to {int(new_volume * 100)}%",is_text_mode)

                elif "decrease volume" in query:
                    current_volume = volume.GetMasterVolumeLevelScalar()
                    new_volume = max(0.0, current_volume - 0.1)
                    volume.SetMasterVolumeLevelScalar(new_volume, None)
                    speakPTX(f"Decreased volume to {int(new_volume * 100)}%",is_text_mode)

                elif "increase brightness" in query:
                    current_brightness = sbc.get_brightness()[0]
                    new_brightness = min(100, current_brightness + 10)
                    sbc.set_brightness(new_brightness)
                    speakPTX(f"Increased brightness to {new_brightness}%",is_text_mode)

                elif "decrease brightness" in query:
                    current_brightness = sbc.get_brightness()[0]
                    new_brightness = max(0, current_brightness - 10)
                    sbc.set_brightness(new_brightness)
                    speakPTX(f"Decreased brightness to {new_brightness}%",is_text_mode)

                elif "cpu usage" in query:
                    cpu_usage = psutil.cpu_percent(interval=1)
                    speakPTX(f"The current CPU usage is {cpu_usage}%",is_text_mode)

                elif "battery status" in query:
                    battery = psutil.sensors_battery()
                    if battery:
                        percent = battery.percent
                        is_plugged = battery.power_plugged
                        status = "plugged in" if is_plugged else "not plugged in"
                        speakPTX(f"The battery is at {percent}% and is {status}.",is_text_mode)
                    else:
                        speakPTX("Unable to retrieve battery status.",is_text_mode)

                elif "turn on airplane mode" in query:
                    os.system("start ms-settings:network-airplanemode")
                    speakPTX("Opening Airplane mode settings.",is_text_mode)

                elif "turn off wifi" in query:
                    os.system("netsh wlan set hostednetwork mode=disallow")
                    speakPTX("Wi-Fi has been turned off.",is_text_mode)

                elif "quit" in query or "exit" in query or "goodbye" in query:
                    print("Exiting...")
                    speakPTX("NIce with you buddy,Stay Connected.",is_text_mode)
                    # sys.exit()

                elif "switch to text input" in query:
                    use_voice_input = False
                    speakPTX("Switched to text input mode. You can now type your commands.",is_text_mode)

                elif "switch to voice input" in query:
                    use_voice_input = True
                    speakPTX("Switched to voice input mode. Listening for your commands.",is_text_mode)

                else:
                    # AI query generation by the Groq API
                    if TURBO:
                        try:
                            response = GenerateGroq(query)
                            print(response)
                            speakPTX(response,is_text_mode)
                            continue
                        except Exception as e:
                            print(e)
                            speakPTX("Sure  you may check your API or the Internet Connection first for Turbo Mode features.",is_text_mode)
                    else:
                        AIquery = speakPTXinput("Sorry sir you need to activate TURBO mode for my capability check. Should I turn on the Turbo mode for you",is_text_mode)
                        if ("turn" in AIquery and "on" in AIquery) or "yes" in AIquery or "activate" in AIquery and "turbo" in AIquery:
                            TURBO = True
                            response = GenerateGroq(query)
                            print(response)
                            speakPTX(response,is_text_mode)
                            continue
            except Exception as e:
                print(e)
