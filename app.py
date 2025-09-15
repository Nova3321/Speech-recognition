import streamlit as st
import speech_recognition as sr
import os

# ---------------------------
# Fonction principale de transcription
# ---------------------------
def transcribe_speech(api_choice, language, paused):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        if paused:
            st.warning("Reconnaissance vocale en pause. Cliquez sur 'Reprendre'.")
            return None

        st.info("🎤 Parlez maintenant...")
        try:
            audio_text = r.listen(source, timeout=5, phrase_time_limit=10)
            st.info("📝 Transcription en cours...")

            if api_choice == "Google":
                text = r.recognize_google(audio_text, language=language)
            elif api_choice == "Sphinx":
                text = r.recognize_sphinx(audio_text, language=language)
            elif api_choice == "Bing Speech (clé API requise)":
                # Exemple si l'utilisateur configure une clé API Bing
                api_key = st.text_input("🔑 Entrez votre clé API Bing")
                if api_key:
                    text = r.recognize_bing(audio_text, key=api_key, language=language)
                else:
                    st.error("Clé API Bing manquante")
                    return None
            else:
                st.error("API non reconnue.")
                return None

            return text

        except sr.UnknownValueError:
            st.error("❌ Je n'ai pas compris l'audio.")
        except sr.RequestError as e:
            st.error(f"⚠️ Erreur de requête vers l'API : {e}")
        except sr.WaitTimeoutError:
            st.warning("⏳ Temps écoulé, aucune voix détectée.")
        except Exception as e:
            st.error(f"Erreur inattendue : {e}")
        return None


# ---------------------------
# Interface Streamlit
# ---------------------------
def main():
    st.title("🎙️ Application de Reconnaissance Vocale Améliorée")

    # Choix de l’API
    api_choice = st.selectbox(
        "Choisissez l'API de reconnaissance vocale :",
        ["Google", "Sphinx", "Bing Speech (clé API requise)"]
    )

    # Choix de la langue
    language = st.selectbox(
        "Choisissez la langue :",
        [
            ("Français - fr-FR"),
            ("Anglais - en-US"),
            ("Arabe - ar-DZ"),
            ("Espagnol - es-ES")
        ]
    )
    lang_code = language.split("-")[-1]  # extrait par ex "fr-FR"

    # Boutons Pause/Reprendre
    if "paused" not in st.session_state:
        st.session_state.paused = False

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⏸️ Pause"):
            st.session_state.paused = True
    with col2:
        if st.button("▶️ Reprendre"):
            st.session_state.paused = False

    # Lancer la transcription
    if st.button("🎤 Commencer la transcription"):
        text = transcribe_speech(api_choice, lang_code, st.session_state.paused)
        if text:
            st.success(f"Texte transcrit : {text}")

            # Sauvegarde du texte dans un fichier
            if st.button("💾 Enregistrer dans un fichier"):
                file_path = "transcription.txt"
                with open(file_path, "a", encoding="utf-8") as f:
                    f.write(text + "\n")
                st.success(f"Texte enregistré dans {os.path.abspath(file_path)} ✅")

# Exécuter l’application
if __name__ == "__main__":
    main()
