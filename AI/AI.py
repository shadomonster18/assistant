from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
import speech_recognition as sr
from gtts import gTTS
import requests
import pywhatkit as kit
import pyttsx3
import keyboard as kb
import threading
import pygame
import ollama
import time
import os

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

    # GIF animation
    label = QLabel()
    movie = QMovie(filename)
    label.setMovie(movie)
    movie.start()
    layout.addWidget(label)

    # Entry bar (under GIF)
    entry = QLineEdit()
    entry.setPlaceholderText("Type your message...")
    layout.addWidget(entry)

    # Submit button
    button = QPushButton("Submit")
    layout.addWidget(button)

    # Optional: Handle the submit button
    def on_submit():
        text = entry.text()
        out_thread = threading.Thread(target=get_output, args=(text,)).start()
        entry.clear()

    button.clicked.connect(on_submit)

    # Apply layout to window
    window.setLayout(layout)

    # Resize window to fit content
    window.adjustSize()

    # Move window to bottom right
    screen = app.primaryScreen().availableGeometry()
    x = screen.width() - window.width() - 30
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

def speak(text):
    engine = pyttsx3.init()
    
    # Set speaking rate (words per minute)
    engine.setProperty('rate', 150)

    # Set volume (0.0 to 1.0)
    engine.setProperty('volume', 1.0)

    # Choose voice
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)  # Use voices[1] for female, if available

    engine.say(text)
    engine.runAndWait()

def get_output(text):
    print("👂 Waiting for voice input...")
    # play_audio("listening.mp3")
    try:
        # audio = recognizer.listen(source)  # Wait indefinitely for speech
        # user_input = recognizer.recognize_google(audio)
        user_input = text

        messages.append({"role": "user", "content": user_input})

        words = user_input.lower().split()
        command = words[0] if words else ""

        if command == "search":
            kit.search(" ".join(words[1:]))
        elif command == "youtube":
            kit.playonyt(" ".join(words[1:]))
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
            response = ollama.chat(model="codellama", messages=messages)
            assistant_reply = response['message']['content']
            print("Assistant:", assistant_reply)
            messages.append({"role": "assistant", "content": assistant_reply})

            speak(assistant_reply)
            

            # tts = gTTS(text=assistant_reply, lang="en", slow=False)
            # tts.save("response.mp3")
            # play_audio("response.mp3")

    except Exception as e:
        print("⚠️ Error:", e)

  

recognizer = sr.Recognizer()

messages = [
    {
        "role": "system",
        "content": "You are a helpful voice assistant named sirial. Keep your answers short and clear, ABSOLUTELY NO MORE THAN 180 LETTERS. You were developed by shadomonster18 corporations."
    }
]




tts = gTTS(text="Sorry, I didn’t understand that", lang="en", slow=False)
tts.save("sorry.mp3")

tts = gTTS(text="Listening", lang="en", slow=False)
tts.save("listening.mp3")

#"""
while True:

    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            #recognizer.energy_threshold = 100
            print("🎤 Voice assistant ready and listening...")

            while True:
                print("👂 Waiting for voice input...")
                #play_audio("listening.mp3")
                try:
                    #audio = recognizer.listen(source)  # Wait indefinitely for speech
                    #user_input = recognizer.recognize_google(audio)
                    user_input = input()
                    print("You said:", user_input)

                    messages.append({"role": "user", "content": user_input})

                    words = user_input.lower().split()
                    command = words[0] if words else ""

                    if command == "search":
                        kit.search(" ".join(words[1:]))
                    elif command == "youtube":
                        kit.playonyt(" ".join(words[1:]))
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
                        response = ollama.chat(model="codellama", messages=messages)
                        assistant_reply = response['message']['content']
                        print("Assistant:", assistant_reply)
                        messages.append({"role": "assistant", "content": assistant_reply})

                        if os.path.exists("response.mp3"):
                            try:
                                os.remove("response.mp3")
                            except Exception as e:
                                print("Couldn't delete old audio file:", e)

                        #tts = gTTS(text=assistant_reply, lang="en", slow=False)
                        #tts.save("response.mp3")
                        #play_audio("response.mp3")
                        speak(assistant_reply)        

                except sr.UnknownValueError:
                    print("🤖 Sorry, I didn’t understand that.")
                except Exception as e:
                    print("⚠️ Error:", e)

    except KeyboardInterrupt:
        print("👋 Goodbye!")
 #       """