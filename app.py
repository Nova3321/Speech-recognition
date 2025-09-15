import streamlit as st
import speech_recognition as sr
import os

# ---------------------------
# Transcription depuis un fichier audio
# ---------------------------
def transcribe_audio_file(api_choice, language, file):
    r = sr.Recognizer()
    with sr.AudioFile(file) as source:
        audio_text = r.record(source)
        try:
            if api_choice == "Google":
                return r.recognize_google(audio_text, language=language)
            elif api_choice == "Sphinx":
                try:
                    return r.recognize_sphinx(audio_text, language=language)
                except:
                    st.error("⚠️ Sphinx non disponible sur Streamlit Cloud.")
                    return None
            else:
                st.error("⚠️ API non supportée dans ce mode.")
                return None
        except sr.UnknownValueError:
            st.error("❌ Impossible de comprendre l’audio.")
        except sr.RequestError as e:
            st.error(f"⚠️ Erreur API : {e}")
    return None

# ---------------------------
# Interface Streamlit
# ---------------------------
def main():
    st.title("🎙️ Application de Reconnaissance Vocale (Compatible Cloud)")

    # Choix de l’API
    api_choice = st.selectbox(
        "Choisissez l'API de reconnaissance vocale :",
        ["Google", "Sphinx"]
    )

    # Choix de la langue
    language = st.selectbox(
        "Choisissez la langue :",
        ["fr-FR", "en-US", "es-ES", "ar-DZ"]
    )

    # Upload fichier audio
    uploaded_file = st.file_uploader("📂 Uploadez un fichier audio (wav/mp3)", type=["wav", "mp3"])

    if uploaded_file is not None:
        st.info("📝 Transcription en cours...")
        text = transcribe_audio_file(api_choice, language, uploaded_file)
        if text:
            st.success(f"Texte transcrit : {text}")

            # Sauvegarde du texte
            if st.button("💾 Enregistrer dans un fichier"):
                file_path = "transcription.txt"
                with open(file_path, "a", encoding="utf-8") as f:
                    f.write(text + "\n")
                st.success(f"Texte enregistré dans {os.path.abspath(file_path)} ✅")

    st.markdown("---")
    st.info("⚠️ Sur Streamlit Cloud, le micro n’est pas disponible. Utilisez l’upload d’un fichier audio. "
            "En local, vous pouvez lancer la version avec `sr.Microphone()`.")

# Exécuter l’application
if __name__ == "__main__":
    main()
