# Import necessary modules for threading, GUI, speech recognition, text-to-speech, API requests, etc.
from concurrent.futures import thread
from imaplib import Commands
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
import speech_recognition as sr
from gtts import gTTS
import requests
try:
    import pywhatkit as kit  # For YouTube and web search functionality
except:
    pass
import pyttsx3
import keyboard as kb
import threading
import pygame
import pyautogui as pg
import ollama  # For LLM chat
import time
import os
import cv2
import torch

# OpenWeatherMap API details
BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
API_KEY = "API_KEY"  # Replace with your actual OpenWeatherMap API key

def get_weather(city):
    """
    Queries the OpenWeatherMap API for weather data in a given city.
    Returns the response as a dictionary.
    """
    url = BASE_URL + "appid=" + API_KEY + "&q=" + city
    response = requests.get(url).json()
    return response

# Load YOLOv5 object detection model from Ultralytics using torch.hub
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

def get_classes():
    """
    Captures an image using the webcam,
    runs YOLOv5 object detection on the captured image,
    and returns a list of detected object class names.
    """
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

    for *box, conf, cls in results.xyxy[0]:  # Iterate through detected objects
        class_name = model.names[int(cls)]
        class_list.append(class_name)
        print(class_name)
    annotated_frame = results.render()[0]
    # Optional: display annotated frame, currently commented out
    return class_list

listen = True  # Flag that could be used for listening loop (not currently used)

def animation(filename):
    """
    Creates and displays a PyQt5 GUI window for the voice assistant.
    Shows a GIF animation, a text entry, and buttons for submitting text or activating voice input.
    """
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
    #layout.addWidget(label)  # GIF currently not added to layout

    # Entry bar (under GIF)
    entry = QLineEdit()
    entry.setPlaceholderText("Type your message...")
    layout.addWidget(entry)

    # Submit button
    button = QPushButton("Submit")
    layout.addWidget(button)
    
    speak = QPushButton("Voice")
    layout.addWidget(speak)
        
    # Handle submit button click: process entered text
    def on_submit():
        text = entry.text()
        out_thread = threading.Thread(target=get_output, args=(text,)).start()
        entry.clear()
    # Handle voice button click: start voice recognition
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
    window.adjustSize()  # Resize window to fit content

    # Move window to bottom right
    screen = app.primaryScreen().availableGeometry()
    x = 30
    y = screen.height() - window.height() - 60
    window.move(x, y)

    window.show()
    sys.exit(app.exec_())

# Launch the GUI in a separate daemon thread
threading.Thread(target=animation, args=("resize.gif",), daemon=True).start()

def play_audio(file):
    """
    Plays an audio file using pygame.
    """
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    pygame.mixer.quit()

def say(text):
    """
    Uses pyttsx3 to speak the given text aloud.
    """
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)     # Set speech rate
    engine.setProperty('volume', 1.0)   # Set volume
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)  # Use voices[1] for female, if available
    engine.say(text)
    engine.runAndWait()

def get_output(text):
    """
    Main function to process user input and execute commands.
    Handles search, YouTube play, weather, camera, file reading, and calls LLM for other queries.
    """
    try:
        user_input = text
        messages.append({"role": "user", "content": user_input})

        words = user_input.lower().split()
        command = words[0] if words else ""

        # Web search using pywhatkit
        if command == "search":
            kit.search(" ".join(words[1:]))
        # Play YouTube video using pywhatkit
        elif command == "youtube":
            kit.playonyt(" ".join(words[1:]))
        # Open application or file using keyboard shortcuts
        elif command == "open":
            kb.press_and_release("windows")
            time.sleep(0.3)
            kb.write(" ".join(words[1:]))
            time.sleep(0.3)
            kb.press_and_release("enter")
        # Get weather using OpenWeatherMap API
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
        # Detect objects using webcam and YOLOv5
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
        # Read contents of file aloud
        elif command == "read":
            with open(" ".join(words[1:]), "r") as file:
                file_text = file.read()
                say(f"The file reads {file_text}") #if len(list(file_text)) < 300 else "File is too long.")
        # Custom web requests for specific keywords
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
            # If command not recognized, use LLM (Ollama) for chat response
            commands = ["search", "youtube", "open", "weather", "camera"]
            if command not in commands:
                response = ollama.chat(model="codellama", messages=messages)
                assistant_reply = response['message']['content']
                print("Assistant:", assistant_reply)
                messages.append({"role": "assistant", "content": assistant_reply})
                say(assistant_reply)
    except Exception as e:
        print("⚠️ Error:", e)

# Speech recognizer instance
recognizer = sr.Recognizer()

# Initial system prompt for LLM
messages = [
    {
        "role": "system",
        "content": "You are a helpful voice assistant named sirial. Keep your answers short and clear, ABSOLUTELY NO MORE THAN 180 LETTERS."
    }
]

# Pre-generate TTS audio files for fallback/error notifications
tts = gTTS(text="Sorry, I didn’t understand that", lang="en", slow=False)
tts.save("sorry.mp3")

tts = gTTS(text="Listening", lang="en", slow=False)
tts.save("listening.mp3")

# Main loop (currently just pass, can be extended for continuous listening)
#"""
while True:
    pass
 #       """
