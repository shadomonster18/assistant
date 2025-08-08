from concurrent.futures import thread
from imaplib import Commands
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
import speech_recognition as sr
from gtts import gTTS
import requests
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

BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
API_KEY = "037ba4f97795497e172cbc0a510c17c0"



def get_weather(city):
    url = BASE_URL + "appid=" + API_KEY + "&q=" + city
    
    response = requests.get(url).json()
    
    return response

model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

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

    cap.release()
    cv2.destroyAllWindows()

    results = model("captured_image.jpg")

    for *box, conf, cls in results.xyxy[0]:
        class_name = model.names[int(cls)]
        #if class_name == 'person':
         #   print("\nHuman detected!")
          #  break
        
        class_list.append(class_name)
        print(class_name)
    annotated_frame = results.render()[0]
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
        
    # Optional: Handle the submit button
    def on_submit():
        text = entry.text()
        out_thread = threading.Thread(target=get_output, args=(text,)).start()
        entry.clear()
    def voice():
        import speech_recognition as sr

        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Say something!")
            say("listening")
            audio = r.listen(source)

        try:
            text = r.recognize_google(audio)
            print("You said: " + text)
            say("got it")
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

def say(text):
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
        user_input = text

        messages.append({"role": "user", "content": user_input})

        words = user_input.lower().split()
        command = words[0] if words else ""

        if command == "search":
            kit.search(" ".join(words[1:]))
        elif command == "youtube":
            kit.playonyt(" ".join(words[1:]))
        elif command == "open":
            kb.press_and_release("windows")
            time.sleep(0.3)
            kb.write(" ".join(words[1:]))
            time.sleep(0.3)
            kb.press_and_release("enter")
        if command == "weather":
            try:
                weather = get_weather(" ".join(words[1:]))
                temp = int(weather["main"]["temp"] - 273)
                feels_like = int(weather["main"]["feels_like"] -273)
                humidity = weather["main"]["humidity"]
                description = weather["weather"][0]["description"]
            
                say(f"The current weather in {' '.join(words[1:])} is {temp} degrees celsius, feels like {feels_like} degrees, with a humidity of {humidity}%, and {description}.")
            except:
                say("a fatal error occured while retrieving weather data.")
        elif command == "camera":
            classes = get_classes()
            classes = list(set(classes))
            print(classes)
            if len(classes) != 0:
                text = f"I can see a {classes[0]}"
                text += f"and a {classes[1]}" if len(classes) > 1 else ""
                text += f"and a {classes[2]}" if len(classes) > 2 else ""
                say(text)
            else:
                say("I dont see anything")
        elif command == "read":
            with open(" ".join(words[1:]), "r") as file:
                file_text = file.read()
                say(f"The file reads {file_text}") #if len(list(file_text)) < 300 else "File is too long.")
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
            commands = ["search", "youtube", "open", "weather", "camera"]
            
            if command not in commands:
                response = ollama.chat(model="codellama", messages=messages)
                assistant_reply = response['message']['content']
                print("Assistant:", assistant_reply)
                messages.append({"role": "assistant", "content": assistant_reply})

                say(assistant_reply)
            

            # tts = gTTS(text=assistant_reply, lang="en", slow=False)
            # tts.save("response.mp3")
            # play_audio("response.mp3")

    except Exception as e:
        print("⚠️ Error:", e)

  

recognizer = sr.Recognizer()

messages = [
    {
        "role": "system",
        "content": "You are a helpful voice assistant named sirial. Keep your answers short and clear, ABSOLUTELY NO MORE THAN 180 LETTERS."
    }
]




tts = gTTS(text="Sorry, I didn’t understand that", lang="en", slow=False)
tts.save("sorry.mp3")

tts = gTTS(text="Listening", lang="en", slow=False)
tts.save("listening.mp3")

#"""
while True:
    pass
 #       """