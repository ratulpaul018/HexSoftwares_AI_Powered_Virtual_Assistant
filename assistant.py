import speech_recognition as sr
import pyttsx3
import pyaudio
import pywhatkit
import datetime
import wikipedia


listener = sr.Recognizer()
listener.energy_threshold = 4000
listener.dynamic_energy_threshold = True
engine = pyttsx3.init()


def talk(text):
    engine.say(text)
    engine.runAndWait()

def input_instruction():
    instruction = ""
    try:
        with sr.Microphone() as source:
            print("Listening... (speak now)")
            # Adjust for ambient noise
            listener.adjust_for_ambient_noise(source, duration=1)
            # Listen for speech with longer timeout
            speech = listener.listen(source, timeout=10, phrase_time_limit=10)
            print("Processing audio...")
            instruction = listener.recognize_google(speech)
            print(f"You said: {instruction}")
            if "ratul" in instruction.lower():
                instruction = instruction.replace("ratul", "").strip()
    except sr.UnknownValueError:
        print("Could not understand audio. Please try again.")
    except sr.RequestError as e:
        print(f"API Error: {e}. Check your internet connection.")
    except Exception as e:
        print(f"Error: {e}")

    return instruction
    

def play_music():
    instruction = input_instruction()

    if not instruction or instruction == "":
        print("No speech detected.")
        talk("Sorry, I didn't catch that.")
        return

    instruction = instruction.lower()
    print(f"You said: {instruction}")

    if "play" in instruction:
        media = instruction.replace("play", "").strip()
        talk("playing " + media)
        try:
            pywhatkit.playonyt(media)
        except Exception as e:
            print(f"Error playing music: {e}")

    elif "time" in instruction:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        talk("Current time is " + current_time)

    elif "date" in instruction:
        current_date = datetime.datetime.now().strftime("%D")
        talk("Today's date is " + current_date)

    elif "who is" in instruction:
        person = instruction.replace("who is", "").strip()
        try:
            info = wikipedia.summary(person, sentences=1)
            talk(info)
        except Exception as e:
            print(f"Error getting info: {e}")
            talk("I couldn't find information about that person.")

    else:
        talk("I didn't understand that.")

if __name__ == "__main__":
    play_music()