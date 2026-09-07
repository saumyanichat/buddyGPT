import streamlit as st
import os

# Audio features are best-effort: they work locally when the required libraries
# and hardware are available, and degrade gracefully on hosted deployments.
try:
    import speech_recognition as sr
    import pyttsx3
    from langdetect import detect
    import sys

    sys.stdout.reconfigure(encoding='utf-8')
    AUDIO_AVAILABLE = True
except Exception:
    sr = None
    pyttsx3 = None
    detect = None
    AUDIO_AVAILABLE = False

def record_audio():
    """Record audio using microphone (works only locally)."""
    if not AUDIO_AVAILABLE:
        st.warning("🎤 Audio input is unavailable in this environment.")
        return ""

    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("🎤 Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
    except Exception as e:
        st.warning(f"🎤 Audio input is unavailable here: {e}")
        return ""

    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand that."
    except sr.RequestError:
        return "Error: Check your internet connection."

def generate_response(text):
    """Detect the language and return the text and language code."""
    if not AUDIO_AVAILABLE or detect is None:
        # Fallback if langdetect is not available.
        return text, 'en'
    
    lang = detect(text)
    return text, lang

def speak_text(text, lang='en'):
    """Speak text aloud using offline TTS (only locally)."""
    if not AUDIO_AVAILABLE:
        st.warning("🔊 Text-to-speech is unavailable in this environment.")
        return

    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)

        # Optional: Set language-specific voice
        voices = engine.getProperty('voices')
        if lang.startswith('hi'):
            for voice in voices:
                if 'hindi' in voice.name.lower() or 'hi' in voice.languages:
                    engine.setProperty('voice', voice.id)
                    break
        elif lang.startswith('en'):
            for voice in voices:
                if 'english' in voice.name.lower():
                    engine.setProperty('voice', voice.id)       
                    break

        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print("🔊 Speech synthesis error:", e)

# Optional test
if __name__ == "__main__":
    user_input = record_audio()
    if user_input and "Sorry" not in user_input and "Error" not in user_input:
        response, lang = generate_response(user_input)
        print(f"Detected language: {lang}")
        print("Bot:", response)
        speak_text(response, lang)



# ⭐ One-Minute Interview Answer

# audio_utils.py manages all voice-related functionality in FeelBuddy. It first checks whether the application is running locally or on a deployed server. If it's deployed on Render, audio features are disabled because cloud servers don't provide microphone or speaker access. For local execution, record_audio() captures the user's speech through the microphone and converts it into text using Google's Speech Recognition API. The detected text is then processed by the chatbot. Finally, speak_text() converts the chatbot's response into speech using the offline pyttsx3 library, selecting an appropriate voice based on the detected language.

# | Question                                            | Short Answer                                                                                                                                                |
# | --------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
# | Why disable audio on Render?                        | Render is a headless cloud server and has no access to physical microphones or speakers.                                                                    |
# | How is speech converted to text?                    | Using the `SpeechRecognition` library with Google's Speech Recognition service.                                                                             |
# | Why call `adjust_for_ambient_noise()`?              | To reduce background noise and improve speech recognition accuracy.                                                                                         |
# | Why use `pyttsx3` instead of an online TTS service? | `pyttsx3` works offline, requires no API key, and avoids network latency for text-to-speech.                                                                |
# | Why detect the language?                            | To choose an appropriate voice and support multilingual conversations.                                                                                      |
# | What happens if speech recognition fails?           | The function catches the exception and returns a user-friendly error message instead of crashing.                                                           |
# | Why keep audio features in a separate file?         | To follow modular design and the Single Responsibility Principle, making the code easier to maintain and reuse.                                             |
# | Does `pyttsx3` require an internet connection?      | No. It is an offline text-to-speech engine, unlike the speech recognition step, which relies on Google's online recognition service in your implementation. |
