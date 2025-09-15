import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import speech_recognition as sr
import av

st.set_page_config(page_title="Reconnaissance Vocale", page_icon="🎤", layout="centered")

# Dictionnaire des langues disponibles
LANGUAGES = {
    "Français": "fr-FR",
    "Anglais": "en-US",
    "Arabe": "ar-SA",
    "Espagnol": "es-ES"
}

st.title("🎤 Application de Reconnaissance Vocale (WebRTC)")
st.write("Parlez directement dans votre micro, le texte transcrit s’affichera ici.")

# Sélecteur de langue
lang_choice = st.selectbox("Choisissez la langue :", list(LANGUAGES.keys()))
lang_code = LANGUAGES[lang_choice]

# Zone de texte transcrit
if "transcription" not in st.session_state:
    st.session_state.transcription = ""


# Classe qui traite l’audio en temps réel
class AudioProcessor(AudioProcessorBase):
    def __init__(self) -> None:
        self.recognizer = sr.Recognizer()

    def recv_audio(self, frame: av.AudioFrame) -> av.AudioFrame:
        # Convertir en tableau numpy
        audio = frame.to_ndarray()

        # Convertir en audio SpeechRecognition
        try:
            with sr.AudioData(audio.tobytes(), frame.sample_rate, 2) as source:
                text = self.recognizer.recognize_google(source, language=lang_code)
                st.session_state.transcription += text + " "
        except sr.UnknownValueError:
            pass  # Pas compris
        except sr.RequestError as e:
            st.error(f"Erreur API : {e}")
        return frame


# Lancement de WebRTC pour capturer le micro
webrtc_streamer(
    key="speech",
    mode=WebRtcMode.SENDONLY,
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"audio": True, "video": False},
)

# Affichage du texte transcrit
st.subheader("📝 Transcription en direct")
st.write(st.session_state.transcription)

# Bouton pour sauvegarder la transcription
if st.button("💾 Enregistrer dans un fichier"):
    with open("transcription.txt", "w", encoding="utf-8") as f:
        f.write(st.session_state.transcription)
    st.success("Texte enregistré dans 'transcription.txt'")
