import streamlit as st
import speech_recognition as sr
import os
from datetime import datetime
import io


# ---------------------------
# Fonction pour initialiser la session
# ---------------------------
def init_session_state():
    if 'transcription' not in st.session_state:
        st.session_state.transcription = ""
    if 'is_listening' not in st.session_state:
        st.session_state.is_listening = False
    if 'pause' not in st.session_state:
        st.session_state.pause = False


# ---------------------------
# Fonction pour sauvegarder la transcription
# ---------------------------
def save_transcription(text):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"transcription_{timestamp}.txt"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)
        return filename
    except Exception as e:
        return f"Erreur lors de la sauvegarde : {str(e)}"


# ---------------------------
# Fonction principale de reconnaissance vocale
# ---------------------------
def transcribe_speech(api_choice, language, audio_source=None):
    r = sr.Recognizer()
    try:
        # Si audio_source est None → micro
        if audio_source is None:
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source)
                st.info("Parlez maintenant...")
                while st.session_state.is_listening and not st.session_state.pause:
                    try:
                        audio_text = r.listen(source, timeout=5, phrase_time_limit=30)
                        st.info("Transcription en cours...")

                        if api_choice == "Google":
                            text = r.recognize_google(audio_text, language=language)
                        elif api_choice == "Sphinx":
                            text = r.recognize_sphinx(audio_text, language=language)
                        elif api_choice == "Wit.ai":
                            text = r.recognize_wit(audio_text, key="VOTRE_CLE_WIT_AI")

                        st.session_state.transcription += text + "\n"
                        st.success("Transcription réussie !")
                        return text
                    except sr.WaitTimeoutError:
                        st.warning("Aucun son détecté. Veuillez parler ou vérifier votre microphone.")
                        continue
                    except sr.UnknownValueError:
                        st.error("Désolé, je n'ai pas compris ce que vous avez dit.")
                        return "Erreur : Parole non reconnue"
                    except sr.RequestError as e:
                        st.error(f"Erreur de l'API {api_choice} : {str(e)}")
                        return f"Erreur API : {str(e)}"
                    except Exception as e:
                        st.error(f"Erreur inattendue : {str(e)}")
                        return f"Erreur : {str(e)}"
        else:
            # Transcription à partir d'un fichier audio uploadé
            audio_bytes = audio_source.read()
            audio_file = sr.AudioFile(io.BytesIO(audio_bytes))
            with audio_file as source:
                r.adjust_for_ambient_noise(source)
                audio_text = r.record(source)

            st.info("Transcription du fichier audio en cours...")
            if api_choice == "Google":
                text = r.recognize_google(audio_text, language=language)
            elif api_choice == "Sphinx":
                text = r.recognize_sphinx(audio_text, language=language)
            elif api_choice == "Wit.ai":
                text = r.recognize_wit(audio_text, key="VOTRE_CLE_WIT_AI")

            st.session_state.transcription += text + "\n"
            st.success("Transcription réussie !")
            return text

    except Exception as e:
        st.error(f"Erreur d'initialisation ou de transcription : {str(e)}")
        return "Erreur d'initialisation ou de transcription"


# ---------------------------
# Interface principale Streamlit
# ---------------------------
def main():
    st.title("Application de Reconnaissance Vocale Améliorée")
    init_session_state()

    # ---------------------------
    # Upload audio
    # ---------------------------
    st.subheader("🔹 Transcrire un fichier audio")
    uploaded_file = st.file_uploader("Choisissez un fichier audio (.wav, .mp3)", type=["wav", "mp3"])
    if uploaded_file:
        api_choice_file = st.selectbox("Choisissez l'API pour le fichier", ["Google", "Sphinx"])
        language_options = {
            "Français": "fr-FR",
            "Anglais (US)": "en-US",
            "Espagnol": "es-ES",
            "Allemand": "de-DE",
            "Italien": "it-IT"
        }
        language_file = st.selectbox("Choisissez la langue pour le fichier", list(language_options.keys()))
        language_code_file = language_options[language_file]

        if st.button("Transcrire le fichier audio"):
            transcribe_speech(api_choice_file, language_code_file, audio_source=uploaded_file)

    st.markdown("---")
    st.subheader("🔹 Reconnaissance vocale avec Microphone (Local uniquement)")

    # Sélection de l'API
    api_options = ["Google", "Sphinx"]
    api_choice = st.selectbox("Choisissez l'API de reconnaissance vocale", api_options, key="api_mic")

    # Sélection de la langue
    language_options = {
        "Français": "fr-FR",
        "Anglais (US)": "en-US",
        "Espagnol": "es-ES",
        "Allemand": "de-DE",
        "Italien": "it-IT"
    }
    language = st.selectbox("Choisissez la langue pour le micro", list(language_options.keys()), key="lang_mic")
    language_code = language_options[language]

    # Boutons de contrôle
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Démarrer la reconnaissance"):
            st.session_state.is_listening = True
            st.session_state.pause = False
            st.session_state.transcription = ""  # Réinitialiser la transcription
            transcribe_speech(api_choice, language_code)

    with col2:
        if st.button("Pause/Reprendre"):
            st.session_state.pause = not st.session_state.pause
            st.info("Reconnaissance en pause" if st.session_state.pause else "Reprise de la reconnaissance")

    with col3:
        if st.button("Arrêter"):
            st.session_state.is_listening = False
            st.session_state.pause = False
            st.info("Reconnaissance arrêtée")

    # Affichage de la transcription
    st.text_area("Transcription", st.session_state.transcription, height=200)

    # Sauvegarde de la transcription
    if st.session_state.transcription and st.button("Sauvegarder la transcription"):
        filename = save_transcription(st.session_state.transcription)
        st.success(f"Transcription sauvegardée dans {filename}")
        with open(filename, "rb") as file:
            st.download_button(
                label="Télécharger la transcription",
                data=file,
                file_name=filename,
                mime="text/plain"
            )

from pydub import AudioSegment
import speech_recognition as sr

def transcribe_large_wav(file_path, language="fr-FR", chunk_ms=30000):
    audio = AudioSegment.from_wav(file_path)
    recognizer = sr.Recognizer()
    transcription = ""

    # Découper l'audio en segments
    for i in range(0, len(audio), chunk_ms):
        chunk = audio[i:i+chunk_ms]
        chunk_io = io.BytesIO()
        chunk.export(chunk_io, format="wav")
        chunk_io.seek(0)

        with sr.AudioFile(chunk_io) as source:
            audio_chunk = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_chunk, language=language)
                transcription += text + " "
            except sr.UnknownValueError:
                transcription += "[Incompréhensible] "
            except sr.RequestError as e:
                transcription += f"[Erreur API : {e}] "

    return transcription

if __name__ == "__main__":
    main()
