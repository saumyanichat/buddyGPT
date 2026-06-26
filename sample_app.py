import streamlit as st
from streamlit_chat import message
from sample_utils import get_initial_message, get_groq_response, update_chat
from audio_utils import record_audio, speak_text
import random
import os
from dotenv import load_dotenv
import translation

def run_genai_chat(name,gender):
    st.set_page_config(
        page_title="FeelBuddy",
        page_icon="python-scripts/favicon.jpg",
    )

    if st.sidebar.button("🔒 Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()  

    load_dotenv()
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    st.markdown(
        f"""
        <style>
        .chat-container {{
            max-width: 600px;
            margin-left: 0;
            padding: 10px;
            border-radius: 10px;
        }}
        .user-message {{
            background-color: skyblue;
            color: black;
            font-size:18px;
            padding: 10px;
            border-radius: 10px;
            max-width: 80%;
            margin: 5px 0;
            float: right;
            clear: both;
        }}
        .bot-message {{
            background-color: #8EC5FC;
            background-image: linear-gradient(62deg, #8EC5FC 0%, #e6c3fc 100%);
            color: black;
            font-size:18px;
            padding: 10px;
            border-radius: 10px;
            max-width: 80%;
            margin: 5px 0;
            float: left;
            clear: both;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title(f"Hello {name}, Buddy 👋🏻")

    if 'generated' not in st.session_state:
        st.session_state['generated'] = []
    if 'past' not in st.session_state:
        st.session_state['past'] = []
    if 'messages' not in st.session_state:
        st.session_state['messages'] = get_initial_message()
    if 'show_video_button' not in st.session_state:
        st.session_state['show_video_button'] = False
    if 'selected_video' not in st.session_state:
        st.session_state['selected_video'] = None
    if 'video_history' not in st.session_state:
        st.session_state['video_history'] = []
    if 'show_music_button' not in st.session_state:
        st.session_state['show_music_button'] = False
    if 'selected_music' not in st.session_state:
        st.session_state['selected_music'] = None
    if 'show_counselor_video_button' not in st.session_state:
        st.session_state['show_counselor_video_button'] = False
    if 'detected_mood' not in st.session_state:
        st.session_state['detected_mood'] = None
    if 'user_language' not in st.session_state:
        st.session_state['user_language'] = None
    if 'audio_chat_enabled' not in st.session_state:
        st.session_state['audio_chat_enabled'] = False
    if 'last_streamed_index' not in st.session_state:
        st.session_state['last_streamed_index'] = -1

    video_suggestions = {
        "sad": ["https://www.youtube.com/watch?v=tCRbVEGHZlQ", "https://www.youtube.com/watch?v=28Kplr_9wxg","https://www.youtube.com/watch?v=iD_tsK_aqIQ"],
        "angry": ["https://www.youtube.com/watch?v=LU-smxT1czo", "https://www.youtube.com/watch?v=xCAML-mh23w"],
        "depressed": ["https://www.youtube.com/watch?v=ooOak5FVkpM", "https://www.youtube.com/watch?v=0Vhe72NMZJc"],
        "bored": ["https://www.youtube.com/watch?v=TvRhfaouBHs", "https://www.youtube.com/watch?v=nTB61iR6cVQ"]
    }

    music_library = {
        "happy": ["https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3"],
        "sad": ["https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3", "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3"],
        "calm": ["https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3", "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3"],
        "energetic": ["https://www.soundhelix.com/examples/mp3/SoundHelix-Song-7.mp3", "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3"]
    }

    counselor_videos = {
        "sad": ["https://www.youtube.com/watch?v=BloutcYWbJg","https://www.youtube.com/watch?v=r79vAZ4XoV8"],
        "angry": ["https://www.youtube.com/watch?v=QAsJvKsd2Xk", "https://www.youtube.com/watch?v=wkse4PPxkk4"],
        "depressed": ["https://www.youtube.com/watch?v=d96akWDnx0w", "https://www.youtube.com/watch?v=Y9A5wuTtblw"]
    }

    negative_mood_keywords = {
        "sad": ["sad", "unhappy", "down", "blue","not okay","not good","bad","not feeling good","not feeling well"],
        "angry": ["angry", "mad", "furious", "annoyed"],
        "depressed": ["depressed", "hopeless", "miserable", "low"],
        "bored": ["bored", "dull", "nothing to do", "lazy"]
    }

    def detect_mood(query):
        for mood, keywords in negative_mood_keywords.items():
            if any(word in query.lower() for word in keywords):
                return mood
        return None

    def is_music_request(query):
        music_keywords = ["play music", "play a song", "play something", "play"]
        return any(keyword in query.lower() for keyword in music_keywords)

    voice_triggered = False

    # Top Voice Button
    if st.button("Start Voice Chatting🎤", key="top_voice_btn"):
        voice_triggered = True

    # Render Chat History Container
    if st.session_state['generated']:
        with st.container():
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for i in range(len(st.session_state['generated'])):
                st.markdown(f"""<div class="user-message">{st.session_state['past'][i]}</div>""", unsafe_allow_html=True)
                
                # Check if this index was already streamed
                if i <= st.session_state.get('last_streamed_index', -1):
                    st.markdown(f"""<div class="bot-message">{st.session_state["generated"][i]}</div>""", unsafe_allow_html=True)
                else:
                    # Stream the latest message word-by-word
                    placeholder = st.empty()
                    words = st.session_state["generated"][i].split(" ")
                    current_text = ""
                    import time
                    for w in words:
                        current_text += w + " "
                        placeholder.markdown(f"""<div class="bot-message">{current_text}</div>""", unsafe_allow_html=True)
                        time.sleep(0.08) # Speak speed (approx 125 WPM)
                    st.session_state['last_streamed_index'] = i

                    # Speak the text aloud after streaming finishes
                    if st.session_state.get('audio_chat_enabled'):
                        speak_text(st.session_state["generated"][i], st.session_state['user_language'])

                if i < len(st.session_state["video_history"]) and st.session_state["video_history"][i]:
                    st.write("📺 Suggested Video:")
                    st.video(st.session_state["video_history"][i])
            st.markdown('</div>', unsafe_allow_html=True)

    # Render Actions (short clip, music, counselor)
    if st.session_state['show_video_button'] and st.button("📺 Watch a short clip"):
        st.session_state.video_history[-1] = st.session_state['selected_video']
        st.video(st.session_state['selected_video'])

    if st.session_state['show_music_button'] and st.button("🎵 Play Music"):
        st.audio(st.session_state['selected_music'], format="audio/mp3")

    if st.session_state['show_counselor_video_button'] and st.session_state['detected_mood']:
        st.write("### 🧠 Counselor Video Recommendation")
        if st.button("📹 Watch Counselor Video"):
            selected_counselor_video = random.choice(counselor_videos[st.session_state['detected_mood']])
            st.video(selected_counselor_video)

    # Render Bottom Microphone Button near search bar (just above st.chat_input)
    cols = st.columns([15, 1])
    with cols[1]:
        if st.button("🎤", key="bottom_mic_btn", help="Start voice chatting"):
            voice_triggered = True

    # Chat Input
    query = st.chat_input("Ask me something...")

    # Handle voice trigger
    if voice_triggered:
        with st.spinner("Listening... Speak now! 🎤"):
            voice_query = record_audio()
        if voice_query and voice_query.strip() and "Sorry" not in voice_query and "Error" not in voice_query:
            query = voice_query
            st.session_state['audio_chat_enabled'] = True
            st.info(f"🎤 Heard: {voice_query}")
        elif voice_query:
            st.warning(voice_query)

    # Process Query (Runs at the bottom and reruns to render the new content instantly)
    if query:
        detected_lang = translation.detect_language(query)
        if st.session_state['user_language'] is None or detected_lang != st.session_state['user_language']:
            st.session_state['user_language'] = detected_lang
        user_lang_name = translation.get_language_name(st.session_state['user_language'])

        with st.spinner("Generating response..."):
            messages = st.session_state['messages']
            messages = update_chat(messages, "user", f"My language is {user_lang_name}. Respond in {user_lang_name} only. Now, my question is: {query}")
            response = get_groq_response(messages) or ""
            if not response.strip():
                response = "I'm sorry, but I couldn't generate a response. Please try again."

            messages = update_chat(messages, "assistant", response)

            response_lang = translation.detect_language(response) if isinstance(response, str) and response else "en"
            if response_lang != st.session_state['user_language']:
                translated_response = translation.translate_text(response, st.session_state['user_language']) or response
            else:
                translated_response = response

            st.session_state.past.append(query)
            st.session_state.generated.append(translated_response)
            st.session_state.video_history.append(None)

            detected_mood = detect_mood(query)
            st.session_state['detected_mood'] = detected_mood
            if detected_mood:
                st.session_state['show_video_button'] = True
                st.session_state['selected_video'] = random.choice(video_suggestions[detected_mood])
                st.session_state['show_counselor_video_button'] = True
            else:
                st.session_state['show_video_button'] = False
                st.session_state['show_counselor_video_button'] = False

            if is_music_request(query):
                st.session_state['show_music_button'] = True
                st.session_state['selected_music'] = random.choice(music_library.get(detected_mood, music_library["happy"]))
            else:
                st.session_state['show_music_button'] = False
            
            st.rerun()




# ⭐ One-Minute Interview Answer
# sample_app.py is the main chatbot module of FeelBuddy. After a user logs in, it initializes the chat interface and manages the entire conversation. 
# It stores chat history using Streamlit Session State, supports both text and voice interactions, detects the user's language for multilingual 
# communication, and sends the conversation history to the Groq Llama 3 model to generate context-aware responses. It also performs simple 
# keyword-based mood detection and recommends videos, music, or counselor resources based on the detected mood. Finally, it updates the chat history 
# and refreshes the interface to display the latest AI response, creating an interactive and personalized mental health support experience.
# 


# ⭐ Most Common Interview Questions
# Question	Short Answer : 

# Why use Session State?  -> To preserve chat history, user preferences, and UI state because Streamlit reruns the script on every interaction.
# Why pass the entire conversation to the LLM?	So the model has context and can generate coherent, conversational responses instead of treating each message independently.
# How does mood detection work?	A keyword-based function checks the user's message for predefined emotional keywords such as "sad", "angry", or "depressed".
# How is multilingual support implemented?	The user's language is detected before the request, and responses are translated back if the LLM returns a different language.
# How does voice chat work?	Speech is converted to text using speech recognition, processed by the chatbot, and the response can be converted back to speech using text-to-speech.
# Why use dictionaries for videos and music?	They provide a simple, fast way to map detected moods to relevant recommendations without requiring additional database queries.
# Why call st.rerun()?	To immediately refresh the Streamlit interface and display the newly generated response.
# How is the AI response generated?	The conversation history is sent to the Groq API using the Llama 3 model, which generates a context-aware reply.