from concurrent.futures import thread
import subprocess as sb
from imaplib import Commands
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
import speech_recognition as sr
from gtts import gTTS
import requests
import shutil
try:
    import pywhatkit as kit
except:
    pass
import pyttsx3
import keyboard as kb
import threading
import pygame
import pyautogui as pg
import ollama
import time
import os
import cv2
import torch
import psutil
import requests
from time import sleep
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyttsx3
import ollama
import shlex



BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
API_KEY = "OPEN_WEATHERMAP_KEY"



def get_weather(city):
    url = BASE_URL + "appid=" + API_KEY + "&q=" + city
    
    response = requests.get(url).json()
    
    return response

_torch_load = torch.load
def torch_load_patch(*args, **kwargs):
    kwargs["weights_only"] = False
    return _torch_load(*args, **kwargs)
torch.load = torch_load_patch

model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
#model.to('cuda')
model.conf = 0.4


def get_classes():
    print("starting")
    
    class_list = []

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        exit()

    ret, frame = cap.read()
    if ret:
        cv2.imwrite("captured_image.jpg", frame)
        print("Image saved as captured_image.jpg")
    else:
        print("Failed to capture image")


    results = model("captured_image.jpg", size=320)
    detections = results.xyxy[0]

    for *box, conf, cls in detections:
        if conf < 0.4:
            continue
        class_name = model.names[int(cls)]
        x1, y1, x2, y2 = map(int, box)

        label = f"{model.names[int(cls)]} {conf:.2f}"
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        #if class_name == 'person':
         #   print("\nHuman detected!")
          #  break
        
        class_list.append(class_name)
        print(class_name)
    #annotated_frame = results.render()[0]

    if ret:
        cv2.imwrite("captured_image.jpg", frame)
        print("Image saved as captured_image.jpg")
    else:
        print("Failed to capture image")

    sb.call("start captured_image.jpg", shell=True)
    cap.release()
    cv2.destroyAllWindows()
    #cv2.imshow("YOLOv5 Detection", annotated_frame)
    #cv2.waitKey(0)
    #0cv2.destroyAllWindows()
    return class_list


listen = True
def animation(filename):
    import sys
    from PyQt5.QtWidgets import QApplication, QLabel
    from PyQt5.QtGui import QMovie
    from PyQt5.QtCore import Qt
    app = QApplication(sys.argv)

    # Main window setup
    window = QWidget()
    window.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
    window.setAttribute(Qt.WA_TranslucentBackground)

    # Layout for stacking GIF, Entry, and Button
    layout = QVBoxLayout()
    layout.setContentsMargins(10, 10, 10, 10)
    layout.setSpacing(5)

    text_label = QLabel('Voice Assistant')
    text_label.setStyleSheet("font-size: 18px; color: lightblue;")
    layout.addWidget(text_label)

    # GIF animation
    label = QLabel()
    movie = QMovie(filename)
    label.setMovie(movie)
    movie.start()
    #layout.addWidget(label)

    # Entry bar (under GIF)
    entry = QLineEdit()
    entry.setPlaceholderText("Type your message...")
    layout.addWidget(entry)

    # Submit button
    button = QPushButton("Submit")
    layout.addWidget(button)
    
    speak = QPushButton("Voice")
    layout.addWidget(speak)
        
    def on_submit():
        text = entry.text()
        out_thread = threading.Thread(target=get_output, args=(text,)).start()
        entry.clear()
    def voice():
        import speech_recognition as sr

        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Say something!")
            say("listening", speak)
            audio = r.listen(source)

        try:
            text = r.recognize_google(audio)
            print("You said: " + text)
            say("got it", speak)
            out_thread = threading.Thread(target=get_output, args=(text,)).start()
        except sr.UnknownValueError:
            print("Sphinx could not understand audio")
        except sr.RequestError as e:
            print("Sphinx error; {0}".format(e))

    def start_voice():
        threading.Thread(target=voice).start()
    button.clicked.connect(on_submit)
    speak.clicked.connect(start_voice)

    # Apply layout to window
    window.setLayout(layout)

    # Resize window to fit content
    window.adjustSize()

    # Move window to bottom right
    screen = app.primaryScreen().availableGeometry()
    x = 30
    y = screen.height() - window.height() - 60
    window.move(x, y)

    window.show()
    sys.exit(app.exec_())

threading.Thread(target=animation, args=("resize.gif",), daemon=True).start()

def play_audio(file):
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    pygame.mixer.quit()

def say(text, shouldSpeak):
    engine = pyttsx3.init()
    
    # set speech rate
    engine.setProperty('rate', 150)

    # set volume
    engine.setProperty('volume', 1.0)

    # voice
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)  # Use voices[1] for female, if available

    engine.say(text)
    engine.runAndWait()

def get_output(text):
    # play_audio("listening.mp3")
    try:
        # audio = recognizer.listen(source)
        # user_input = recognizer.recognize_google(audio)
        speak = True

        user_input = text

        if "-no-speak" in user_input.lower():
                    user_input = user_input.lower().replace("-no-speak", "")
                    speak = False

        messages.append({"role": "user", "content": user_input})

        words = user_input.lower().split()
        command = words[0] if words else ""

        # commmands
        if command == "search":
            kit.search(" ".join(words[1:]))
        elif command == "youtube":
            kit.playonyt(" ".join(words[1:]))
        elif command == "open":
            #os.startfile(" ".join(words[1:]))
            kb.press_and_release("windows")
            time.sleep(0.3)
            kb.write(" ".join(words[1:]))
            time.sleep(0.3)
            kb.press_and_release("enter")

            '''
            apps = {
                "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",

                }

            #os.startfile(" ".join(words[1:]))
            try:
                sb.call(f'start "" "{ " ".join(words[1:]) }"', shell=True)
            except Exception as e:
                try:
                    sb.call(f'start "" "{ apps[" ".join(words[1:]).lower()] }"', shell=True)
                except:
                    say("application not found", speak)
                    '''
            return
        
        if command == "weather":
            try:
                weather = get_weather(" ".join(words[1:]))
                temp = int(weather["main"]["temp"] - 273)
                feels_like = int(weather["main"]["feels_like"] -273)
                humidity = weather["main"]["humidity"]
                description = weather["weather"][0]["description"]
            
                say(f"The current weather in {' '.join(words[1:])} is {temp} degrees celsius, feels like {feels_like} degrees, with a humidity of {humidity}%, and {description}.", speak)
            except:
                say("a fatal error occured while retrieving weather data.")
        elif command == "system-stats":
            cpu = psutil.cpu_percent(interval=1)
            memory = round(psutil.virtual_memory().total / (1024 ** 3), 1)
            available_memory = round(psutil.virtual_memory().available / (1024 ** 3), 1)
            disk = round(psutil.disk_usage('/').total / (1024 ** 3), 1)
            used = round(psutil.disk_usage('/').used / (1024 ** 3), 1)

            message = f"CPU Usage: {cpu}%, available RAM: {available_memory}GB, total RAM: {memory}GB, total SSD: {disk}GB, SSD used: {used}GB"

            print(message)
            say(message, speak)
        elif command == "cnn":
            url = "https://www.edition.cnn.com/search?q="
            search = user_input.lower().replace("cnn", "")

            # Set up Chrome options for headless browsing
            options = webdriver.ChromeOptions()
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-blink-features=AutomationControlled')

            driver = webdriver.Chrome(options=options)
            driver.get(url+search)

            sleep(7)
            try:

                cookies = driver.find_element(By.XPATH, "//*[contains(text(), 'Accept All')]")
                cookies.click()
            except:
                print("no cookies")
            sleep(3)
            label = driver.find_element(By.XPATH, "//*[contains(text(), 'Stories')]")
            label.click()

            sleep(2)

            try:
                title = driver.find_element(By.CLASS_NAME, "container__headline-text")
                title.click()
            except:
                print("no articles found")

      
            article_element = driver.find_element(By.CSS_SELECTOR, 'div.article__content')

             # Extract and print the article text
            article_text = article_element.text
            driver.quit()

            news_messages = [
                {
                    "role": "system",
                    "content": "summarize the contents of this article in a few lines."
                }
            ]

            news_messages.append({"role": "user", "content": article_text})

            print(article_text + "\n\n\n\n\n")
            response = ollama.chat(model="codellama", messages=news_messages)
            assistant_reply = response['message']['content']

            print("Assistant:", assistant_reply)
            news_messages.append({"role": "assistant", "content": assistant_reply})
            say(assistant_reply, True)


        elif command == "camera":
            classes = get_classes()
            classes = list(set(classes))
            print(classes)
            if len(classes) != 0:
                text = f"I can see a {classes[0]}"
                
                text += f"and a {classes[1]}" if len(classes) > 1 else ""
                text += f"and a {classes[2]}" if len(classes) > 2 else ""
                say(text, speak)
            else:
                say("I dont see anything", speak)
        elif command == "stream":
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                exit()

            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                results = model(frame, size=320)
                annotated_frame = results.render()[0]
                cv2.imshow("YOLOv5 Webcam Stream", annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        elif command == "move-files":
            num_files_moved = 0
            parts = shlex.split(user_input)

            try:
                search_folder = parts[1]
                target_folder = parts[2]
                file_extension = parts[3]
                for file in os.listdir(search_folder):
                    if file.endswith(file_extension):
                        origin = os.path.join(search_folder, file)
                        destination = os.path.join(target_folder, file)
                        shutil.move(origin, destination)
                        num_files_moved += 1
                        print("moved " + file + " to " + destination)
            except Exception as e:
                print(e)
                say("failed", speak)
        elif command == "read":
            with open(" ".join(words[1:]), "r") as file:
                file_text = file.read()
                say(f"The file reads {file_text}", speak) #if len(list(file_text)) < 300 else "File is too long.")
        elif user_input.lower() == "one":
            requests.get('https://shadomonster18.pythonanywhere.com/song/rickroll')
        elif user_input.lower() == "two":
            requests.get('https://shadomonster18.pythonanywhere.com/song/lion')
        elif user_input.lower() == "three":
            requests.get('https://shadomonster18.pythonanywhere.com/song/Canon')
        elif user_input.lower() == "led":
            requests.get('https://shadomonster18.pythonanywhere.com/song/led on')
        elif user_input.lower() == "off":
            
            requests.get('https://shadomonster18.pythonanywhere.com/song/off')
        else:
            commands = ["search", "youtube", "open", "weather", "camera", "cnn", "move-files", "stream"]
            
            if command not in commands:

                response = ollama.chat(model="codellama", messages=messages)
                assistant_reply = response['message']['content']
                print("Assistant:", assistant_reply)             
                messages.append({"role": "assistant", "content": assistant_reply})

                if speak:
                    say(assistant_reply, speak)
            

            # tts = gTTS(text=assistant_reply, lang="en", slow=False)
            # tts.save("response.mp3")
            # play_audio("response.mp3")    it 

    except Exception as e:
        print("⚠️ Error:", e)

  

recognizer = sr.Recognizer()

messages = [
    {
        "role": "system",
        "content": "You are a helpful voice assistant named sirial. Keep your answers short and clear, ABSOLUTELY NO MORE THAN 180 LETTERS."
    }
]




#tts = gTTS(text="Sorry, I didn’t understand that", lang="en", slow=False)
#tts.save("sorry.mp3")

#tts = gTTS(text="Listening", lang="en", slow=False)
#tts.save("listening.mp3")

#"""
while True:
    pass
 #       """
