import os
import sys
import datetime
import pyttsx3
import platform
import subprocess
import socket
import speech_recognition as sr
from rich.console import Console
import webbrowser
import speedtest
import whisper
import requests  
import webbrowser
import json

def get_config_file_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')

# Function to load the current configuration from the JSON file
def load_config():
    config_file_path = get_config_file_path()

    # Check if the file exists and load it
    if os.path.exists(config_file_path):
        with open(config_file_path, 'r') as f:
            return json.load(f)
    else:
        print("Config file not found. Creating a default one.")
        # Return a default config if file is missing
        return {"Settings": {"music_directory": "", "weather_api_key": "", "ai_model": ""}}

# Load the configuration
config = load_config()

# Access the settings
music_directory = config['Settings']['music_directory']
weather_api_key = config['Settings']['weather_api_key']
model = config['Settings']['ai_model']


sys.stderr = open(os.devnull, 'w')

color = Console()

conversation_history = []

engine = pyttsx3.init()

weather_q = {
    "weather of"
}

time_q = {
    "what's the time",
    "what time is it",
    "tell me the time",
    "can you tell me the time",
    "please tell the time",
    "what is the time",
    "what is the time going on",
    "what's the time going on"
}

shutdown_q = {
    "shutdown the pc"
}

restart_q = {
    "restart the pc"
}

internet = [
    "check the internet",
    "internet status"
]

check_connection = [
    "what is the speed of the internet",
    "what is the speed of the internet",
    "check the speed of internet",
    "check the internet speed",
]

websearch_q = [
    "search for",
    "look up",
    "search"
]

def say(text):
    """Text-to-Speech function."""
    engine.say(text)
    engine.runAndWait()

def check_internet():
    """Check if the machine is connected to the internet."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except (socket.timeout, socket.gaierror):
        return False

def takeCommand():
    """Take command using Google Speech-to-Text API."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening with Google...")
        try:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source, timeout=30, phrase_time_limit=30)
            query = r.recognize_google(audio, language="en-in")
            print(f"User said: {query}")
            return query.lower()
        except sr.UnknownValueError:
            say("Sorry, I couldn't understand that. Could you please repeat?")
            return None  
        except sr.RequestError:
            say("Sorry, there was an issue with the speech recognition service.")
            return None 
        except Exception as e:
            say(f"Sorry, I encountered an error: {e}")
            return None  

def takeCommandOffline():
    """Take command using Whisper for offline speech recognition."""
    try:
        model = whisper.load_model("base")
        print("Listening with Whisper...")
        with sr.Microphone() as source:
            r = sr.Recognizer()
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source, timeout=30, phrase_time_limit=30)

            print("Processing audio with Whisper...")
            temp_path = "temp_audio.wav"
            with open(temp_path, "wb") as f:
                f.write(audio.get_wav_data())

            result = model.transcribe(temp_path, language="en")  # Specify language
            os.remove(temp_path)  # Clean up temporary audio file

            query = result["text"]
            print(f"User said: {query}")
            return query.lower()
    except Exception as e:
        say(f"Sorry, I encountered an error: {e}")
        return None
    



def current_day_and_date():
    today = datetime.datetime.now()
    return today.strftime("Today is %A, %d %B %Y")

def yesterday_and_tomorrow():
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    tomorrow = today + datetime.timedelta(days=1)
    return (
        yesterday.strftime("Yesterday was %A, %d %B %Y"),
        tomorrow.strftime("Tomorrow will be %A, %d %B %Y"),
    )

def last_occurrence_of_day(day_name):
    today = datetime.datetime.now()
    day_name = day_name.capitalize()
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    if day_name not in days_of_week:
        return f"'{day_name}' is not a valid day."
    day_index = days_of_week.index(day_name)
    days_back = (today.weekday() - day_index) % 7
    last_day = today - datetime.timedelta(days=days_back)
    return last_day.strftime(f"The last {day_name} was on %A, %d %B %Y.")

def next_occurrence_of_day(day_name):
    today = datetime.datetime.now()
    day_name = day_name.capitalize()
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    if day_name not in days_of_week:
        return f"'{day_name}' is not a valid day."
    day_index = days_of_week.index(day_name)
    days_forward = (day_index - today.weekday()) % 7
    next_day = today + datetime.timedelta(days=days_forward)
    return next_day.strftime(f"The next {day_name} is on %A, %d %B %Y.")

def day_of_week_for_date(date_str):
    try:
        specific_date = datetime.datetime.strptime(date_str, "%d %B %Y")
        return specific_date.strftime(f"The day on {date_str} is %A.")
    except ValueError:
        return "Invalid date format. Please use 'dd Month yyyy', e.g., '12 December 2024'."


def web_search(query):
    """Perform a web search on Google."""
    try:
        search_query = query.split("search for", 1)[1].strip()  # Extract the search term
        say(f"Searching for {search_query}")
        search_url = f"https://www.google.com/search?q={search_query}"
        webbrowser.open(search_url)  # Open the search results in the default browser
        say(f"Showing results for {search_query}")
    except Exception as e:
        say(f"Sorry, I couldn't perform the search. Error: {e}")

def get_weather(city):
    """Fetch weather information for the city."""
    api_key = weather_api_key  # Replace with your API key
    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    try:
        # Print the full URL for debugging
       

        response = requests.get(base_url)
        
        # Check if the response is valid
        if response.status_code == 200:
            data = response.json()
            
            # Debug the data response
           

            if data.get("cod") == 200:
                main = data["main"]
                weather = data["weather"][0]
                temp = main["temp"]
                humidity = main["humidity"]
                description = weather["description"]
                weather_info = f"Temperature: {temp}°C, Humidity: {humidity}%, Description: {description.capitalize()}"
                return weather_info
            else:
                return f"Sorry, I couldn't find weather information for {city}. Please check the city name."
        else:
            return f"Error: Unable to fetch data (Status code: {response.status_code})"

    except Exception as e:
        return f"Error: {e}"

def aura(query):
    """AI query handler connecting to localhost:11434."""
    global conversation_history
    try:
        print("Aura AI is thinking...")

        # Append the user's query to the conversation history
        conversation_history.append({"role": "user", "content": query})

        # Define the API endpoint
        url = "http://localhost:11434/api/chat"

        # Prepare the payload
        payload = {
            "model": f"{model}",  # Replace with your specific model name
            "messages": conversation_history,
            "stream": False  # Set to True if you want to handle streaming responses
        }

        # Send the POST request
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})

        # Check if the response is successful
        if response.status_code == 200:
            # Parse the AI response
            ai_message = response.json().get("message", {})
            ai_response = ai_message.get("content", "").strip()
            if not ai_response:
                raise ValueError("No response from AI model.")

            # Append the AI's response to the conversation history
            conversation_history.append({"role": "assistant", "content": ai_response})

            # Display the AI's response
            color.print(f"[cyan]{ai_response}[/cyan]")
            say(ai_response)
            return ai_response
        else:
            raise ValueError(f"Error from server: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: Unable to connect to the AI model. Details: {e}")
        return f"Error: {e}"

def open_and_wait(target):
    """Handles opening an app or file and waits for it to close."""
    try:
        # Extract the app name from the 'apps' dictionary
        app_name = [key for key, value in apps.items() if value == target][0].capitalize()

        say(f"Opening {app_name}")  # Say just the app name (e.g., "Opening Word")
        
        if platform.system() == "Windows":
            process = subprocess.Popen(target, shell=True)

        process.wait()  # Wait for the process to finish
        say(f"{app_name} closed successfully.")
        return  # Prevent AI query handling after app closure
    except Exception as e:
        say(f"Sorry, I couldn't open {target}. Error: {e}")
        return  # Prevent AI query handling after an error

def open_website(website):
    """Opens the website in the default web browser."""
    try:
        website_name = [key for key, value in websites.items() if value == website][0].capitalize()  # Get just the domain name (e.g., "YouTube")

        say(f"Opening {website_name}")  # Say just the website name
        webbrowser.open(website)  # Open the website in the default browser
        say(f"{website_name} opened successfully.")
    except Exception as e:
        say(f"Sorry, I couldn't open {website}. Error: {e}")

def check_connection_speed():
    st = speedtest.Speedtest()
    
    # Get the best server based on ping
    st.get_best_server()
    
    # Measure download and upload speed
    download_speed = st.download() / 1_000_000  # Convert from bits/sec to Mbps
    upload_speed = st.upload() / 1_000_000  # Convert from bits/sec to Mbps
    
    # Measure ping
    ping = st.results.ping
    
    return download_speed, upload_speed, ping

def play_song(song_name, music_directory):
    """Plays the song from the music directory."""
    song_path = os.path.join(music_directory, f"{song_name}.mp3")
    if os.path.exists(song_path):
        try:
            say(f"Playing {song_name}")
            subprocess.Popen(["start", song_path], shell=True)
            return f"Playing {song_name}"
        except Exception as e:
            say(f"Sorry, I encountered an error while playing {song_name}. Error: {e}")
            return f"Error playing {song_name}: {e}"
    else:
        say(f"Sorry, {song_name} not found.")
        return f"Error: {song_name} not found"

if __name__ == '__main__':
    print('Welcome to Aura AI')
    say("Aura AI With The Most Aura")

    apps = {
        "notepad": "notepad",
        "calculator": "calc",
        "word": "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
        "powerpoint": "C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.EXE",
        "excel": "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE"
    }

    websites = {
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "facebook": "https://www.facebook.com",
        "twitter": "https://www.twitter.com",
        "github": "https://www.github.com"
    }

    if check_internet():
        print("Internet is available, using Google Speech-to-Text.")
    else:
        print("No internet detected, using Whisper.")

    while True:
        if check_internet():
            query = takeCommand()  
        else:
            query = takeCommandOffline()  

        if query is None:
            continue  

        if query == "shutdown aura":
            say("Aura is shutting down.")
            break

        app_opened = False
        for app_name, app_cmd in apps.items():
            if app_name in query:
                open_and_wait(app_cmd)
                app_opened = True
                break

        if app_opened:
            continue  # Skip AI query handling if an application was opened

        website_opened = False
        for website_name, website_url in websites.items():
            if website_name in query:
                open_website(website_url)
                website_opened = True
                break

        if website_opened:
            continue  # Skip AI query handling if a website was opened

        if query.lower().startswith("play "):
            song_name = query[5:].strip()
            play_song(song_name) 

        elif any(phrase in query for phrase in time_q):
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            say(f"The time is {current_time}")
        
        elif any(phrase in query for phrase in shutdown_q):
            say("Shutting down your PC in 10 seconds")
            os.system("shutdown /s /t 10")
        
        elif any(phrase in query for phrase in restart_q):
            say("Restarting your PC in 10 seconds")
            os.system("shutdown /r /t 10")
        
        elif any(phrase in query for phrase in internet):
            if check_internet():
                say("You are connected to the internet")
            else:
                say("You are not connected to the internet")

        if "what is today's date" in query:
            result = current_day_and_date()
            color.print(f"[cyan]{result}[/cyan]")
            say(result)

        elif "what is yesterday's date" in query or "what was yesterday" in query:
            result, _ = yesterday_and_tomorrow()
            color.print(f"[cyan]{result}[/cyan]")
            say(result)

        elif "what is tomorrow's date" in query or "what is tomorrow" in query:
            _, result = yesterday_and_tomorrow()
            color.print(f"[cyan]{result}[/cyan]")
            say(result)

        elif "what is the date of last" in query:
            day_name = query.split("last")[-1].strip()
            result = last_occurrence_of_day(day_name)
            color.print(f"[cyan]{result}[/cyan]")
            say(result)

        elif "what is the date of next" in query:
            day_name = query.split("next")[-1].strip()
            result = next_occurrence_of_day(day_name)
            color.print(f"[cyan]{result}[/cyan]")
            say(result)

        elif "what day is on" in query:
            date_str = query.split("what day is")[-1].strip()
            result = day_of_week_for_date(date_str)
            color.print(f"[cyan]{result}[/cyan]")
            say(result)
        
        elif any(phrase in query for phrase in check_connection):
            download_speed, upload_speed, ping = check_connection_speed()
            color.print(f"[cyan]Download speed: {download_speed:.2f} Mbps[/cyan]")
            color.print(f"[cyan]Upload speed: {upload_speed:.2f} Mbps[/cyan]")
            color.print(f"[cyan]Ping: {ping} ms[/cyan]")
            say(f"Download speed: {download_speed:.2f} Mbps, Upload speed: {upload_speed:.2f} Mbps, Ping: {ping} ms")
        
        elif "weather of" in query:
            city = query.replace("weather of", "").strip()
            weather_info = get_weather(city)
            color.print(f"[cyan]{weather_info}[/cyan]")
            say(weather_info)
        
        elif any(phrase in query for phrase in websearch_q):
            web_search(query)

        elif query:
            aura(query)  # Run Aura AI for any other query
