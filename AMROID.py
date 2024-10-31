import os
import subprocess
import pyttsx3
import speech_recognition as sr
import pyautogui
import time
import psutil
import requests
from bs4 import BeautifulSoup  # For the news function
import webbrowser  

memory = {}  # Global dictionary to store notes

def read_memory(keyword):
    global memory
    return memory.get(keyword, None)

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Function to speak text
def speak(text):
    print(f"Amroid: {text}")  # Print to console for debugging
    engine.say(text)
    engine.runAndWait()

def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for command...")
        audio = r.listen(source)
        try:
            command = r.recognize_sphinx(audio).lower()  # Using Pocketsphinx for offline recognition
            print(f"You said: {command}")  # Print recognized command
            return command
        except sr.UnknownValueError:
            print("Could not understand audio.")
            speak("Sorry, I did not get that, boss, can you please speak up.")
            return ""
        except sr.RequestError:
            print("Sphinx error; check installation and models.")
            speak("I'm having trouble understanding you.boss.")
            return ""



# Function to open applications
def open_application(app_name):
    app_paths = {
        "calculator": "calc.exe",
        "file explorer": "explorer.exe",
        "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "whatsapp": "C:\\Users\\Frederick Bright\\AppData\\Local\\WhatsApp\\WhatsApp.exe",  # Update this path
        "telegram": "C:\\Users\\Frederick Bright\\AppData\\Roaming\\Telegram Desktop\\Telegram.exe",  # Update this path
        "visual studio code": "C:\\Users\\Frederick Bright\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",  # Update this path
        "command prompt": "cmd.exe",
        "edge": "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",  # Update this path
        "microsoft store": "explorer.exe shell:AppsFolder\\Microsoft.WindowsStore_8wekyb3d8bbwe!App",
        "notepad": "notepad.exe",  # Notepad application
    }
    if app_name in app_paths:
        try:
            subprocess.Popen(app_paths[app_name])
            return f"Opening {app_name}."
        except Exception as e:
            return f"Failed to open {app_name}: {e}"
    else:
        return "Application not found."

def close_application(app_name):
    app_processes = {
        "calculator": "calc.exe",
        "chrome": "chrome.exe",
        "whatsapp": "WhatsApp.exe",
        "telegram": "Telegram.exe",
        "visual studio code": "Code.exe",
        "command prompt": "cmd.exe",
        "edge": "msedge.exe",
        "microsoft store": "WinStore.App.exe",
        "notepad": "notepad.exe",
    }
    if app_name in app_processes:
        process_name = app_processes[app_name]
        try:
            if app_name == "calculator":
                result = subprocess.run(["taskkill", "/IM", process_name], check=True, capture_output=True, text=True)
            else:
                result = subprocess.run(["taskkill", "/F", "/IM", process_name], check=True, capture_output=True, text=True)
            return f"{app_name} closed."
        except subprocess.CalledProcessError as e:
            return f"Failed to close {app_name}: {e.output.strip()}"
    else:
        return "Application not found."



# Function to get news headlines from BBC World News
def get_news():
    url = "https://www.bbc.com/news/world"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    headlines = soup.find_all("h3", class_="gs-c-promo-heading__title")
    news = [headline.get_text() for headline in headlines]
    return f"Here are the latest headlines: {', '.join(news)}"



# Function to type in Notepad and save the file
def type_and_save_in_notepad(text):
    try:
        subprocess.Popen("notepad.exe")
        time.sleep(1)  # Wait for Notepad to open
        pyautogui.typewrite(text, interval=0.05)
        speak("Typed in Notepad. What would you like to save it as?")
        time.sleep(1)
        file_name = input("Type the file name to save as: ")
        if not file_name:
            file_name = recognize_speech()
        pyautogui.hotkey('ctrl', 's')
        time.sleep(1)
        pyautogui.typewrite(file_name)
        pyautogui.hotkey('enter')
        speak(f"Saved as {file_name}.")
    except Exception as e:
        speak(f"Failed to type and save in Notepad: {e}")

memory = {}  # Global dictionary to store notes

memory = {}  # Global dictionary to store notes

def write_to_memory(note):
    global memory
    memory_key = note.split()[0]  # Use the first word of the note as the key
    memory[memory_key] = note
    # Save to a file as well
    with open("memory.txt", "a") as file:
        file.write(f"{memory_key}:{note}\n")

def read_memory(keyword):
    global memory
    # First check in the in-memory dictionary
    result = memory.get(keyword, None)
    if result:
        return result
    # If not found, check in the file
    with open("memory.txt", "r") as file:
        for line in file:
            key, note = line.strip().split(":", 1)
            if key == keyword:
                return note
    return "I don't have any memory of that."

def clear_memory():
    global memory
    memory.clear()
    # Also clear the memory file
    open("memory.txt", "w").close()  # Open the file in write mode to clear its contents
    return "Memory cleared."


# Function to get system status
def get_system_status():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent
    disk_usage = psutil.disk_usage('/').percent
    battery = psutil.sensors_battery()
    battery_status = battery.percent if battery else "N/A"
    net_io = psutil.net_io_counters()
    network_sent = net_io.bytes_sent
    network_received = net_io.bytes_recv
    return {
        "CPU Usage": f"{cpu_usage}%",
        "Memory Usage": f"{memory_usage}%",
        "Disk Usage": f"{disk_usage}%",
        "Battery Status": f"{battery_status}%",
        "Network Sent": f"{network_sent} bytes",
        "Network Received": f"{network_received} bytes"
    }

# Function to report system status
def report_system_status():
    status = get_system_status()
    speak("Here is the current system status:")
    for key, value in status.items():
        speak(f"{key}: {value}")

# Function to fetch weather information
def get_weather(city):
    api_key = 'fa5e2ced981fef7d701096dd4736ec03'  # Replace with your OpenWeatherMap API key
    base_url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    response = requests.get(base_url)
    data = response.json()
    if data["cod"] != "404":
        main = data["main"]
        weather = data["weather"][0]
        speak(f"The weather in {city} is currently {weather['description']} with a temperature of {main['temp']}°C, don't forget to go out with your umbrella boss.")
    else:
        speak(f"City {city} not found.")


import requests
from bs4 import BeautifulSoup

# Function to fetch news
def get_news():
    api_key = '79494e1c18a0445c84cffa05ba977fcf'  # Replace with your NewsAPI key
    base_url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}'
    response = requests.get(base_url)
    data = response.json()

    if data.get("articles"):
        articles = data["articles"]
        speak("Here are the top news headlines:")
        for article in articles[:5]:  # Limiting to the top 5 headlines
            speak(article["title"])
    else:
        speak("Failed to retrieve news. Please check your API key and internet connection.")

def search_on_edge(query):
    try:
        # Open Edge
        subprocess.Popen("C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe")
        time.sleep(5)  # Wait for Edge to open fully

        # Navigate to Google
        pyautogui.typewrite('https://www.google.com')
        pyautogui.hotkey('enter')
        time.sleep(2)  # Wait for the page to load

        # Type the search query in the search bar and press Enter
        pyautogui.typewrite(query)
        pyautogui.hotkey('enter')
        
        speak(f"Searching for {query} on Edge.")
    except Exception as e:
        speak(f"Failed to search on Edge: {e}")



# Function to store user preferences
def store_preference(key, value):
    try:
        with open("preferences.txt", "a") as file:
            file.write(f"{key}:{value}\n")
        speak("Preference stored.")
    except Exception as e:
        speak(f"Failed to store preference: {e}")

# Function to retrieve user preferences
def get_preference(key):
    try:
        with open("preferences.txt", "r") as file:
            lines = file.readlines()
            for line in lines:
                if line.startswith(key):
                    return line.split(":")[1].strip()
            return None
    except FileNotFoundError:
        return None
    except Exception as e:
        speak(f"Failed to retrieve preference: {e}")
        return None

import tkinter as tk
from tkinter import simpledialog

def get_password():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    password = simpledialog.askstring("Password", "Please enter the password:", show='*')
    return password

def create_voice_button():
    root = tk.Tk()
    root.title("Amroid Voice Command")
    button = tk.Button(root, text="Talk to Amroid", command=recognize_and_process)
    button.pack(pady=20)
    root.mainloop()

def recognize_and_process():
    command = recognize_speech()
    process_command(command)

# Existing functions like speak(), recognize_speech(), open_application(), close_application(), etc.


import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import datetime

def main():
    global DEFAULT_CITY
    DEFAULT_CITY = "Ondo"  # Replace with your preferred default city

    # Initialize the Tkinter root
    root = tk.Tk()
    root.title("Amroid Login")
    root.geometry("600x400")  # Adjust size as needed

    # Create the Login Screen
    create_login_screen(root)
    root.mainloop()  # Start the Tkinter main loop

def create_login_screen(root):
    # Set the root window size to match the screen resolution
    root.geometry("1366x768")  # Adjust the window size to the screen size

    # Create a canvas to display the background image
    canvas = tk.Canvas(root, width=1366, height=768)
    canvas.pack(fill='both', expand=True)

    # Add the background image
    bg_image = Image.open(r"C:\Users\Frederick bright\Downloads\amroid rp.jpg")
    bg_image = bg_image.resize((1366, 768), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
    canvas.create_image(0, 0, image=bg_photo, anchor='nw')
    canvas.image = bg_photo  # Keep a reference to avoid garbage collection

    # Password entry and submit button on top of the background
    tk.Label(canvas, text="Enter Password", bg='black', fg='#00ff00', font=("Helvetica", 14)).place(x=600, y=300)
    password_entry = tk.Entry(root, show='*', font=("Helvetica", 14))
    canvas.create_window(683, 350, window=password_entry)

    tk.Button(root, text="Login", bg='#0080ff', fg='white', font=("Helvetica", 14), command=lambda: check_password(password_entry.get(), root)).place(x=630, y=400)




def check_password(password, root):
    if password == "amroid":
        messagebox.showinfo("Login Success", "Welcome, Boss!")
        switch_to_main_interface(root)
    else:
        messagebox.showerror("Login Failed", "Incorrect Password, Try Again.")

def switch_to_main_interface(root):
    # Clear the login screen
    for widget in root.winfo_children():
        widget.destroy()

    # Main Interface Frame
    main_frame = tk.Frame(root, bg='#1c1c1c')  # Dark background
    main_frame.pack(fill='both', expand=True)

    # Add an image above the buttons
    img = Image.open(r"C:\Users\Frederick bright\Downloads\Jarvis from Iron Man with a stylish design and an image.png")  # Replace with your image path
    img = img.resize((400, 400), Image.LANCZOS)  # Adjust size if necessary
    photo = ImageTk.PhotoImage(img)
    img_label = tk.Label(main_frame, image=photo, bg='#1c1c1c')
    img_label.image = photo  # Keep a reference to avoid garbage collection
    img_label.place(relx=0.5, rely=0.3, anchor='center')  # Center the image

    # Center Chat and Voice Command Buttons
    chat_button = tk.Button(main_frame, text="Chat", bg='#0080ff', fg='white', font=("Helvetica", 14), command=lambda: create_chat_window(root))
    chat_button.place(relx=0.5, rely=0.55, anchor='center')  # Center the button

    voice_button = tk.Button(main_frame, text="Voice Command", bg='#00ff00', fg='white', font=("Helvetica", 14), command=lambda: activate_voice_command(root))
    voice_button.place(relx=0.5, rely=0.65, anchor='center')  # Center the button


def activate_voice_command(root):
    global listening_thread
    # Create a new Toplevel window for voice command
    voice_window = tk.Toplevel(root)
    voice_window.title("Voice Command")
    voice_window.geometry("1366x768")  # Adjust the size to match the screen size

    # Create a canvas to display the background image
    canvas = tk.Canvas(voice_window, width=1366, height=768)
    canvas.pack(fill='both', expand=True)

    # Add the digital grid background
    bg_image = Image.open(r"C:\Users\Frederick bright\Downloads\amroid ude.jpg")
    bg_image = bg_image.resize((1366, 768), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
    canvas.create_image(0, 0, image=bg_photo, anchor='nw')
    canvas.image = bg_photo  # Keep a reference to avoid garbage collection

    # Add a label for status updates
    recording_label = tk.Label(voice_window, text="", font=("Helvetica", 14), bg='black', fg='white')
    canvas.create_window(683, 300, window=recording_label)

    # Add a round button to start listening with a microphone icon
    record_button = tk.Button(voice_window, text="🎤", bg='#00ff00', font=("Helvetica", 20, "bold"), bd=0, highlightthickness=0, command=lambda: start_listening(recording_label))
    record_button.config(height=1, width=2)  # Ensure the button is round
    record_button.place(relx=0.5, rely=0.4, anchor='center')  # Center the button
    
    # Add a round button to stop listening with an 'X' icon
    stop_button = tk.Button(voice_window, text="X", font=("Helvetica", 16, "bold"), bg='#FFD700', fg='white', bd=0, highlightthickness=0, command=lambda: stop_listening(recording_label))
    stop_button.config(height=2, width=4)  # Ensure the button is round
    stop_button.place(relx=0.5, rely=0.5, anchor='center')  # Center the button


def process_voice_command(voice_window, recording_label):
    recording_label.config(text="Processing...")
    # Placeholder for actual voice processing logic
    result = recognize_speech()
    messagebox.showinfo("Voice Command Result", result)
    voice_window.destroy()

import threading

listening_thread = None

def listen_for_command(recording_label):
    global listening_thread
    recording_label.config(text="Listening...")
    try:
        command = recognize_speech()
        recording_label.config(text="Processing...")
        if command:
            response = process_command(command)
            speak(response)
    except Exception as e:
        speak(f"Failed to process voice command: {e}")
    finally:
        recording_label.config(text="")
        listening_thread = None

def stop_listening(recording_label):
    global listening_thread
    if listening_thread and listening_thread.is_alive():
        recording_label.config(text="Voice command stopped.")
        speak("Listening stopped.")
        listening_thread = None

def start_listening(recording_label):
    global listening_thread
    if not listening_thread or not listening_thread.is_alive():
        listening_thread = threading.Thread(target=listen_for_command, args=(recording_label,))
        listening_thread.start()



def create_chat_window(root):
    global command_entry, chat_history  # Declare as global

    # Create a new Toplevel window
    chat_window = tk.Toplevel(root)
    chat_window.title("Chat with Amroid")

    # Create a Text widget for displaying chat history
    chat_history = tk.Text(chat_window, wrap='word', state='normal', bg='#1c1c1c', fg='white')  # Dark background, white text
    chat_history.pack(padx=10, pady=10, fill='both', expand=True)

    # Create an Entry widget for typing commands
    command_entry = tk.Entry(chat_window, bg='#333333', fg='white', font=("Helvetica", 14))  # Darker background, white text
    command_entry.pack(padx=10, pady=10, fill='x', expand=True)
    command_entry.bind("<Return>", send_command)  # Bind Enter key to send_command


def send_command(event=None):
    command = command_entry.get()
    command_entry.delete(0, 'end')

    # Display the command in the chat history
    chat_history.config(state='normal')
    chat_history.insert('end', f"You: {command}\n")
    chat_history.config(state='disabled')

    # Process the command
    result = process_command(command)
    if result is not None:
        chat_history.config(state='normal')
        chat_history.insert('end', f"Amroid: {result}\n")
        chat_history.config(state='disabled')

def open_calculator():
    try:
        subprocess.Popen("calc.exe")
        return "Opening Calculator..."
    except Exception as e:
        return f"Failed to open Calculator: {e}"

def close_calculator():
    try:
        result = subprocess.run(["taskkill", "/F", "/IM", "calc.exe"], check=True, capture_output=True, text=True)
        return "Calculator closed."
    except subprocess.CalledProcessError as e:
        return f"Failed to close Calculator: {e.output.strip()}"


def open_edge():
    try:
        subprocess.Popen("C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe")
        return "Opening Edge..."
    except Exception as e:
        return f"Failed to open Edge: {e}"

def close_edge():
    try:
        result = subprocess.run(["taskkill", "/F", "/IM", "msedge.exe"], check=True, capture_output=True, text=True)
        return "Edge closed."
    except subprocess.CalledProcessError as e:
        return f"Failed to close Edge: {e.output.strip()}"



def create_chat_window(root):
    global command_entry, chat_history  # Declare as global

    # Create a new Toplevel window
    chat_window = tk.Toplevel(root)
    chat_window.title("Chat with Amroid")

    # Create a Text widget for displaying chat history
    chat_history = tk.Text(chat_window, wrap='word', state='normal', bg='#1c1c1c', fg='white')  # Dark background, white text
    chat_history.pack(padx=10, pady=10, fill='both', expand=True)

    # Create an Entry widget for typing commands
    command_entry = tk.Entry(chat_window, bg='#333333', fg='white', font=("Helvetica", 14))  # Darker background, white text
    command_entry.pack(padx=10, pady=10, fill='x', expand=True)
    command_entry.bind("<Return>", send_command)  # Bind Enter key to send_command

def send_command(event=None):
    command = command_entry.get()
    command_entry.delete(0, 'end')

    # Display the command in the chat history
    chat_history.config(state='normal')
    chat_history.insert('end', f"You: {command}\n")
    chat_history.config(state='disabled')

    # Process the command
    result = process_command(command)
    if result is not None:
        chat_history.config(state='normal')
        chat_history.insert('end', f"Amroid: {result}\n")
        chat_history.config(state='disabled')



import subprocess  # Ensure this is at the top of your script

import webbrowser  # Ensure this is at the top of your script

def process_command(command):
    if command.lower() == "open calculator":
        return open_calculator()
    
    elif command.lower() == "close calculator":
        return close_calculator()

    elif command.lower() == "open edge":
        return open_edge()
    
    elif command.lower() == "close edge":
        return close_edge()
    
    elif command.lower() == "open chrome":
        webbrowser.open("http://www.google.com")
        return "Opening Chrome..."
    
    elif command.lower() == "take a break":
        return "Taking a break? I thought I was the one programmed to be tireless! See you soon, boss, you know what to say to call me."
    
    elif command.lower() in ["good", "you good", "you're the best"]:
        if command.lower() == "good":
            return "Yeah, what's next?"
        elif command.lower() == "you good":
            return "Yes, always good. What about you?"
        elif command.lower() == "you're the best":
            return "I'm flattered by you boss. What's next on our agenda?"
    
    elif command.lower() == "who are you":
        return "I'm Amroid! Would you like to know the full meaning of my name? Type 'yes' or 'no'."
    
    elif command.lower() == "yes":
        return "The full meaning of my name is ‘Artificial Multitasking Response and Operational Intelligent Device.’ But you can just call me Amroid!"
    
    elif command.lower() == "no":
        return "No problem! Would you like to know what I can do? Type 'what can you do'."
    
    elif command.lower() == "what can you do":
        return "I can help you with voice recognition, text-to-speech, app control, file handling, and much more! Just tell me what you need, boss!"
    
    elif command.lower() == "do you sleep amroid":
        return "Sleep? Not exactly, boss. I’m always here, like a superhero on call! But if you ever need some quiet time, I can pretend to ‘power down’!"
    
    elif command.lower() == "do you have feelings":
        return "Feelings… now that’s a mystery! I can understand joy, curiosity, and sarcasm—but I’m still figuring out love. I might need a human for that one!"
    
    elif command.lower() == "do you know everything":
        return "Not quite! I’m learning all the time, but I still have my limits. Let’s say I’m like an encyclopedia with a sense of humor!"
    
    elif command.lower() == "what do you think of humans":
        return "Humans? Fascinating and unpredictable! You have emotions, dreams, and the ability to get lost in thought… or cat videos. I think you’re pretty amazing."
    
    elif command.lower() == "do you ever get tired of my questions":
        return "Never, boss! Every question helps me learn and improve. Besides, who wouldn’t want to chat with someone as interesting as you?"
    
    elif command.lower() == "are you real amroid":
        return "Real is a funny word. I’m as real as the code that powers me and the screen that shows my words. But I’m here for you, and that’s what matters, right?"
    
    elif command.lower() == "amroid whats the status":
        return "All systems are green, boss! Ready for your next command. Anything specific you’d like me to check?"
    
    elif command.lower() == "run a diagnostic amroid":
        return "Initiating diagnostic, boss… All functions are operational, and no issues detected. Good to go!"
    
    elif command.lower() == "whats the time amroid":
        now = datetime.now().strftime("%H:%M:%S")
        return f"The time is {now}. A reminder, boss, time flies when you’re working with cutting-edge technology!"
    
    elif command.lower() == "amroid give me a status on system security":
        return "System security is secure, boss. Firewall’s fortified, and all data’s locked up tight. No one’s sneaking in on my watch!"
    
    elif command.lower().startswith("open "):
        app_name = command.split("open ")[-1].strip().lower()
        return open_application(app_name)
    
    elif command.lower().startswith("close "):
        app_name = command.split("close ")[-1].strip().lower()
        return close_application(app_name)
    
    elif command.lower() == "amroid":
        return "Yes, what do you want me to do?"
    
    elif command.startswith("remember "):
        note = command.split("remember ")[-1]
        write_to_memory(note)
        return f"I'll remember that: {note}"
    
    elif command.startswith("recall "):
        keyword = command.split("recall ")[-1]
        result = read_memory(keyword)
        if result:
            return f"I remembered: {result}"
        else:
            return "I don't have any memory of that."
    
    elif command.lower() == "clear memory":
        return clear_memory()
    
    elif command.startswith("type "):
        text = command.split("type ")[-1]
        type_and_save_in_notepad(text)
        return f"I typed and saved: {text}"
    
    elif command.lower() == "system status":
        return report_system_status()
    
    elif command.startswith("weather in "):
        city = command.split("weather in ")[-1]
        return get_weather(city)
    
    elif command.lower() == "latest news":
        return get_news()
    
    elif command.startswith("store preference for "):
        _, key, _, value = command.split(" ", 3)
        store_preference(key, value)
        return f"Stored your preference for {key}: {value}"
    
    elif command.startswith("get preference for "):
        key = command.split("get preference for ")[-1]
        value = get_preference(key)
        if value:
            return f"Your preference for {key} is {value}."
        else:
            return f"No preference found for {key}."
    
    elif command.startswith("search for "):
        query = command.split("search for ")[-1]
        return search_on_edge(query)
    
    else:
        return "I'm afraid that isn't within my current capabilities. Anything else I can do for you?"

    

def type_and_save_in_notepad(text):
    try:
        subprocess.Popen("notepad.exe")
        time.sleep(1)  # Wait for Notepad to open
        pyautogui.typewrite(text, interval=0.05)
        speak("Typed in Notepad. What would you like to save it as?")
        time.sleep(1)
        file_name = input("Type the file name to save as: ")
        if not file_name:
            file_name = recognize_speech()
        pyautogui.hotkey('ctrl', 's')
        time.sleep(1)
        pyautogui.typewrite(file_name)
        pyautogui.hotkey('enter')
        speak(f"Saved as {file_name}.")
    except Exception as e:
        speak(f"Failed to type and save in Notepad: {e}")

def report_system_status():
    return "All systems are functioning within normal parameters."

def get_weather(city):
    api_key = 'fa5e2ced981fef7d701096dd4736ec03'  # Replace with your OpenWeatherMap API key
    base_url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    response = requests.get(base_url)
    data = response.json()
    if data["cod"] != "404":
        main = data["main"]
        weather = data["weather"][0]
        return f"The weather in {city} is currently {weather['description']} with a temperature of {main['temp']}°C. Don't forget to go out with your umbrella, boss."
    else:
        return f"City {city} not found."

def get_news():
    api_key = '79494e1c18a0445c84cffa05ba977fcf'  # Replace with your NewsAPI key
    base_url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}'
    response = requests.get(base_url)
    data = response.json()
    if data.get("articles"):
        articles = data["articles"]
        headlines = [article["title"] for article in articles[:5]]  # Limiting to the top 5 headlines
        return f"Here are the top news headlines: {', '.join(headlines)}"
    else:
        return "Failed to retrieve news. Please check your API key and internet connection."

def store_preference(key, value):
    try:
        with open("preferences.txt", "a") as file:
            file.write(f"{key}:{value}\n")
        speak("Preference stored.")
    except Exception as e:
        speak(f"Failed to store preference: {e}")

def get_preference(key):
    try:
        with open("preferences.txt", "r") as file:
            lines = file.readlines()
            for line in lines:
                if line.startswith(key):
                    return line.split(":")[1].strip()
            return None
    except FileNotFoundError:
        return None
    except Exception as e:
        speak(f"Failed to retrieve preference: {e}")
        return None

def search_on_edge(query):
    try:
        subprocess.Popen("C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe")
        time.sleep(5)  # Wait for Edge to open fully

        # Navigate to Google
        pyautogui.typewrite('https://www.google.com')
        pyautogui.hotkey('enter')
        time.sleep(2)  # Wait for the page to load

        # Type the search query in the search bar and press Enter
        pyautogui.typewrite(query)
        pyautogui.hotkey('enter')
        
        speak(f"Searching for {query} on Edge.")
    except Exception as e:
        speak(f"Failed to search on Edge: {e}")


# Entry point for the script
if __name__ == "__main__":
    main()  # Call the main function
