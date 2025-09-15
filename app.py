```python
import streamlit as st
import speech_recognition as sr
from datetime import datetime
import os


# Fonction pour initialiser la session
def init_session_state():
    if 'transcription' not in st.session_state:
        st.session_state.transcription = ""
    if 'is_listening' not in st.session_state:
        st.session_state.is_listening = False
    if 'pause' not in st.session_state:
        st.session_state.pause = False


# Fonction pour sauvegarder la transcription
def save_transcription(text):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"transcription_{timestamp}.txt"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)
        return filename
    except Exception as e:
        return f"Erreur lors de la sauvegarde : {str(e)}"


# Fonction de reconnaissance vocale
def transcribe_speech(api_choice, language):
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=1)
            st.info("Parlez maintenant...")
            while st.session_state.is_listening and not st.session_state.pause:
                try:
                    audio_text = r.listen(source, timeout=5, phrase_time_limit=30)
                    st.info("Transcription en cours...")

                    if api_choice == "Google":
                        text = r.recognize_google(audio_text, language=language)
                    elif api_choice == "Sphinx":
                        text = r.recognize_sphinx(audio_text)

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
    except Exception as e:
        st.error(f"Erreur d'initialisation du microphone : {str(e)}")
        return f"Erreur : {str(e)}"


# Interface principale Streamlit
def main():
    st.title("Application de Reconnaissance Vocale Améliorée")
    init_session_state()

    # Sélection de l'API
    api_options = ["Google", "Sphinx"]
    api_choice = st.selectbox("Choisissez l'API de reconnaissance vocale", api_options)

    # Sélection de la langue
    language_options = {
        "Français": "fr-FR",
        "Anglais (US)": "en-US",
        "Espagnol": "es-ES",
        "Allemand": "de-DE",
        "Italien": "it-IT"
    }
    language = st.selectbox("Choisissez la langue", list(language_options.keys()))
    language_code = language_options[language]

    # Boutons de contrôle
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Démarrer la reconnaissance"):
            st.session_state.is_listening = True
            st.session_state.pause = False
            st.session_state.transcription = ""
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


if __name__ == "__main__":
    main()