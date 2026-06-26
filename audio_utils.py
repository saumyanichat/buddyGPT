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
