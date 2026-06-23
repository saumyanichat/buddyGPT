import streamlit as st
import os

# Check if running on Render (or similar headless server)
IS_DEPLOYMENT = os.environ.get("RENDER", "false").lower() == "true"

# Only import audio modules if running locally
if not IS_DEPLOYMENT:
    import speech_recognition as sr
    import pyttsx3
    from langdetect import detect
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

def record_audio():
    """Record audio using microphone (works only locally)."""
    if IS_DEPLOYMENT:
        st.warning("🎤 Audio input is disabled in deployment.")
        return ""
    
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand that."
    except sr.RequestError:
        return "Error: Check your internet connection."

def generate_response(text):
    """Detect the language and return the text and language code."""
    if IS_DEPLOYMENT:
        # Fallback if langdetect not available
        return text, 'en'
    
    from langdetect import detect
    lang = detect(text)
    return text, lang

def speak_text(text, lang='en'):
    """Speak text aloud using offline TTS (only locally)."""
    if IS_DEPLOYMENT:
        st.warning("🔊 Text-to-speech is disabled in deployment.")
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
