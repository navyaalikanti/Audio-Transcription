import streamlit as st
import time
import whisper
import pyaudio
import numpy as np
import wave
import os
from deep_translator import GoogleTranslator
from langdetect import detect
import streamlit as st
import time

# Function to display the home page
def show_home():
    # Custom styling for the home page
    st.markdown("""
    <style>
        body {
            background-color: #1E1E1E;
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)

    # Display the title and subtitle
    st.markdown('<h1 style="text-align:center; font-size:48px; font-weight:bold; color:transparent; background:linear-gradient(45deg, #FF5733, #FFC300, #33A1FF); -webkit-background-clip: text;">🎙 Audio Transcription & Translation 🎵</h1>', unsafe_allow_html=True)
    st.markdown('<h3 style="text-align:center; font-size:24px; color:#33A1FF;">Transcribe, Detect, and Translate Effortlessly!</h3>', unsafe_allow_html=True)

    # Use columns to center the button
    col1, col2, col3 = st.columns([1.8, 1.55, 1])  # Column widths to center the button
    with col2:
        # Create a colorful button without custom CSS
        button = st.button("Start Exploring", key="start_exploring")
        
        # When the button is clicked, move to the app page
        if button:
            with st.spinner('Loading...'):
                time.sleep(2)  # Simulate loading time
            st.session_state.page = "app"  # Set session state to "app" page



# Function for the transcription and translation app page
def app_page():
    # Load Whisper model
    model = whisper.load_model("base")

    # Language code mapping for Deep Translator
    LANGUAGE_CODES = {"English": "en", "Hindi": "hi", "Telugu": "te"}

    # Function to record live audio
    def record_audio(output_file="live_audio.wav", record_seconds=5, sample_rate=16000):
        """Record audio from microphone and save to a file."""
        audio_format = pyaudio.paInt16
        channels = 1
        chunk = 1024

        audio = pyaudio.PyAudio()
        stream = audio.open(format=audio_format, channels=channels,
                            rate=sample_rate, input=True,
                            frames_per_buffer=chunk)

        st.write("🎤 Recording... Speak now!")
        frames = []
        for _ in range(0, int(sample_rate / chunk * record_seconds)):
            data = stream.read(chunk)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        audio.terminate()

        with wave.open(output_file, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(audio.get_sample_size(audio_format))
            wf.setframerate(sample_rate)
            wf.writeframes(b''.join(frames))

        return output_file

    # Function to transcribe audio
    def transcribe_audio(file_path):
        """Transcribes an audio file and ensures correct language handling."""
        result = model.transcribe(file_path)
        detected_language = result["language"]
        original_text = result["text"]

        # Translate the transcription if needed
        english_transcription = (
            GoogleTranslator(source=detected_language, target="en").translate(original_text)
            if detected_language in ["hi", "te"]
            else original_text
        )

        translated_text = GoogleTranslator(source=detected_language, target="en").translate(original_text)

        return {
            "original_text": original_text,
            "english_transcription": english_transcription,
            "detected_language": detected_language.upper(),
            "translated_text": translated_text
        }

    # Function to process typed text and detect language
    def process_text(text):
        """Detects language and translates the text to English."""
        detected_lang = detect(text)
        translated_text = GoogleTranslator(source=detected_lang, target="en").translate(text)
        return {
            "original_text": text,
            "detected_language": detected_lang.upper(),
            "translated_text": translated_text
        }

    # Streamlit UI with Background and Title Styling
    st.markdown("""
        <style>
            body {
                background-color: #1E1E1E;
                color: white;
            }
            .title {
                text-align: center;
                font-size: 42px;
                font-weight: bold;
                background: -webkit-linear-gradient(45deg, #FF5733, #FFC300, #33A1FF);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .subtitle {
                text-align: center;
                font-size: 22px;
                color: #33A1FF;
            }
            .container {
                text-align: center;
            }
        </style>
        <div class="container">
            <h1 class="title">🎙 Audio Transcription & Translation 🎵</h1>
            <h3 class="subtitle">Transcribe, Detect, and Translate Effortlessly!!</h3>
        </div>
        <hr>
    """, unsafe_allow_html=True)

    # Input selection (No HTML)
    choice = st.radio("Select Input Method:", 
                    ["📂 Upload File", "🎤 Live Speech", "⌨ Type Text"], 
                    format_func=lambda x: x, key="input_choice")

    # Upload File Option
    if choice == "📂 Upload File":
        uploaded_file = st.file_uploader("Upload an audio or video file", 
                                        type=["mp3", "wav", "mp4", "mov"], key="file_upload")
        
        if uploaded_file is not None:
            with open("temp_input_file", "wb") as f:
                f.write(uploaded_file.read())

            st.write("⏳ Processing...")
            start_time = time.time()

            result = transcribe_audio("temp_input_file")

            st.markdown("<h3 style='color:#FF5733;'>🔹 Original Transcription</h3>", unsafe_allow_html=True)
            st.write(result["original_text"])

            st.markdown("<h3 style='color:#33A1FF;'>🔹 English Transcription</h3>", unsafe_allow_html=True)
            st.write(result["english_transcription"])

            st.markdown("<h3 style='color:#28A745;'>🌍 Detected Language</h3>", unsafe_allow_html=True)
            st.write(f"{result['detected_language']}")

            st.markdown("<h3 style='color:#FFC300;'>📝 English Translation</h3>", unsafe_allow_html=True)
            st.write(result["translated_text"])

            st.audio("temp_input_file")

            st.success(f"✅ Done! (Processing Time: {round(time.time() - start_time, 2)}s)")
            os.remove("temp_input_file")

    # Live Speech Option
    elif choice == "🎤 Live Speech":
        if st.button("Start Recording"):
            st.write("⏳ Processing...")
            start_time = time.time()

            audio_file = record_audio()
            result = transcribe_audio(audio_file)

            st.markdown("<h3 style='color:#FF5733;'>🔹 Original Transcription</h3>", unsafe_allow_html=True)
            st.write(result["original_text"])

            st.markdown("<h3 style='color:#33A1FF;'>🔹 English Transcription</h3>", unsafe_allow_html=True)
            st.write(result["english_transcription"])

            st.markdown("<h3 style='color:#28A745;'>🌍 Detected Language</h3>", unsafe_allow_html=True)
            st.write(f"{result['detected_language']}")

            st.markdown("<h3 style='color:#FFC300;'>📝 English Translation</h3>", unsafe_allow_html=True)
            st.write(result["translated_text"])

            st.audio(audio_file)

            st.success(f"✅ Done! (Processing Time: {round(time.time() - start_time, 2)}s)")
            os.remove(audio_file)

    # Text Input Option
    elif choice == "⌨ Type Text":
        user_text = st.text_area("Type your text here:")
        
        if st.button("Translate"):
            if user_text.strip():
                result = process_text(user_text)

                st.markdown("<h3 style='color:#FF5733;'>🔹 Original Text</h3>", unsafe_allow_html=True)
                st.write(result["original_text"])

                st.markdown("<h3 style='color:#28A745;'>🌍 Detected Language</h3>", unsafe_allow_html=True)
                st.write(f"{result['detected_language']}")

                st.markdown("<h3 style='color:#FFC300;'>📝 English Translation</h3>", unsafe_allow_html=True)
                st.write(result["translated_text"])

                st.success("✅ Done!")
            else:
                st.warning("⚠ Please enter text to translate!")


# Main function to run the app
def main():
    # Check session state for navigation
    if "page" not in st.session_state:
        st.session_state.page = "home"  # Default to home page

    if st.session_state.page == "home":
        show_home()  # Show home page
    elif st.session_state.page == "app":
        app_page()  # Show the transcription app page


# Run the app
if __name__ == "__main__":
    main()
