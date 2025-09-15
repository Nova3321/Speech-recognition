import streamlit as st
import speech_recognition as sr
from datetime import datetime
import os
import threading
import time

# Configuration de la page
st.set_page_config(
    page_title="Reconnaissance Vocale Améliorée",
    page_icon="🎙️",
    layout="wide"
)

# Initialisation des variables d'état
if 'transcribed_text' not in st.session_state:
    st.session_state.transcribed_text = ""
if 'is_listening' not in st.session_state:
    st.session_state.is_listening = False
if 'pause_listening' not in st.session_state:
    st.session_state.pause_listening = False
if 'recognition_thread' not in st.session_state:
    st.session_state.recognition_thread = None

# Dictionnaire des APIs disponibles avec leurs configurations
APIS = {
    "Google": {"function": "recognize_google", "requires_key": False},
    "Google Cloud": {"function": "recognize_google_cloud", "requires_key": True},
    "Sphinx": {"function": "recognize_sphinx", "requires_key": False},
    "Wit.ai": {"function": "recognize_wit", "requires_key": True},
    "Microsoft Bing": {"function": "recognize_bing", "requires_key": True},
    "IBM Speech to Text": {"function": "recognize_ibm", "requires_key": True},
}

# Liste des langues supportées (quelques exemples)
LANGUAGES = {
    "Français": "fr-FR",
    "Anglais (États-Unis)": "en-US",
    "Anglais (Royaume-Uni)": "en-GB",
    "Espagnol": "es-ES",
    "Allemand": "de-DE",
    "Italien": "it-IT",
    "Portugais": "pt-BR",
    "Chinois Mandarin": "zh-CN",
    "Japonais": "ja-JP",
    "Arabe": "ar-EG"
}


def transcribe_speech(api_name, language, api_key=None):
    """Fonction pour transcrire la parole avec gestion d'erreurs améliorée"""
    r = sr.Recognizer()
    r.pause_threshold = 0.8  # Temps d'inactivité pour considérer la fin d'une phrase
    r.energy_threshold = 300  # Seuil de sensibilité au son

    try:
        with sr.Microphone() as source:
            # Ajustement du bruit ambiant
            st.info("Ajustement au bruit ambiant...")
            r.adjust_for_ambient_noise(source, duration=0.5)

            st.info("Parlez maintenant...")
            audio_text = r.listen(source, timeout=5, phrase_time_limit=10)
            st.info("Transcription en cours...")

            # Sélection de l'API à utiliser
            if api_name == "Google":
                text = r.recognize_google(audio_text, language=language)
            elif api_name == "Google Cloud":
                if not api_key:
                    raise ValueError("Clé API Google Cloud manquante")
                text = r.recognize_google_cloud(audio_text, credentials_json=api_key, language=language)
            elif api_name == "Sphinx":
                text = r.recognize_sphinx(audio_text, language=language)
            elif api_name == "Wit.ai":
                if not api_key:
                    raise ValueError("Clé API Wit.ai manquante")
                text = r.recognize_wit(audio_text, key=api_key)
            elif api_name == "Microsoft Bing":
                if not api_key:
                    raise ValueError("Clé API Bing manquante")
                text = r.recognize_bing(audio_text, key=api_key)
            elif api_name == "IBM Speech to Text":
                if not api_key:
                    raise ValueError("Clé API IBM manquante")
                text = r.recognize_ibm(audio_text, username=api_key['username'], password=api_key['password'])
            else:
                raise ValueError("API non supportée")

            return text

    except sr.WaitTimeoutError:
        return "Délai d'attente dépassé. Aucune parole détectée."
    except sr.UnknownValueError:
        return "Impossible de comprendre l'audio"
    except sr.RequestError as e:
        return f"Erreur de service: {e}"
    except Exception as e:
        return f"Erreur inattendue: {e}"


def recognition_loop(api_name, language, api_key=None):
    """Boucle de reconnaissance continue"""
    while st.session_state.is_listening and not st.session_state.pause_listening:
        text = transcribe_speech(api_name, language, api_key)
        if text and not text.startswith("Erreur"):
            timestamp = datetime.now().strftime("%H:%M:%S")
            st.session_state.transcribed_text += f"[{timestamp}] {text}\n"

        # Petit délai pour éviter la surcharge CPU
        time.sleep(0.1)


def save_transcription():
    """Sauvegarde la transcription dans un fichier"""
    if st.session_state.transcribed_text:
        filename = f"transcription_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(st.session_state.transcribed_text)
        return filename
    return None


# Interface utilisateur
st.title("🎙️ Application de Reconnaissance Vocale Améliorée")
st.markdown("---")

# Configuration des colonnes
col1, col2 = st.columns([1, 2])

with col1:
    st.header("Configuration")

    # Sélection de l'API
    selected_api = st.selectbox(
        "Sélectionnez l'API de reconnaissance vocale",
        options=list(APIS.keys()),
        help="Choisissez le service de reconnaissance vocale à utiliser"
    )

    # Champ pour la clé API si nécessaire
    api_key = None
    if APIS[selected_api]["requires_key"]:
        if selected_api == "IBM Speech to Text":
            st.subheader("Identifiants IBM")
            ibm_username = st.text_input("Nom d'utilisateur IBM", type="password")
            ibm_password = st.text_input("Mot de passe IBM", type="password")
            if ibm_username and ibm_password:
                api_key = {"username": ibm_username, "password": ibm_password}
        else:
            api_key = st.text_input(f"Clé API {selected_api}", type="password")

    # Sélection de la langue
    selected_language = st.selectbox(
        "Sélectionnez la langue",
        options=list(LANGUAGES.keys()),
        index=0,
        help="Sélectionnez la langue parlée pour améliorer la précision de reconnaissance"
    )
    language_code = LANGUAGES[selected_language]

    # Paramètres avancés
    with st.expander("Paramètres avancés"):
        adjust_threshold = st.checkbox("Ajuster automatiquement le seuil de sensibilité", value=True)
        if not adjust_threshold:
            sensitivity = st.slider("Sensibilité du microphone", 0, 1000, 300)

    st.markdown("---")

    # Boutons de contrôle
    col1_1, col1_2, col1_3 = st.columns(3)

    with col1_1:
        if not st.session_state.is_listening:
            if st.button("🎤 Démarrer l'écoute", use_container_width=True):
                st.session_state.is_listening = True
                st.session_state.pause_listening = False
                # Démarrer la reconnaissance dans un thread séparé
                st.session_state.recognition_thread = threading.Thread(
                    target=recognition_loop,
                    args=(selected_api, language_code, api_key)
                )
                st.session_state.recognition_thread.start()
                st.rerun()
        else:
            if st.button("⏸️ Pause", use_container_width=True):
                st.session_state.pause_listening = True
                st.rerun()

    with col1_2:
        if st.session_state.is_listening and st.session_state.pause_listening:
            if st.button("▶️ Reprendre", use_container_width=True):
                st.session_state.pause_listening = False
                st.rerun()

    with col1_3:
        if st.session_state.is_listening:
            if st.button("⏹️ Arrêter", use_container_width=True):
                st.session_state.is_listening = False
                st.session_state.pause_listening = False
                if st.session_state.recognition_thread:
                    st.session_state.recognition_thread.join(timeout=1.0)
                st.rerun()

    # Bouton de sauvegarde
    if st.button("💾 Sauvegarder la transcription", use_container_width=True):
        filename = save_transcription()
        if filename:
            st.success(f"Transcription sauvegardée sous: {filename}")
        else:
            st.warning("Aucun texte à sauvegarder")

    # Bouton pour effacer
    if st.button("🗑️ Effacer la transcription", use_container_width=True):
        st.session_state.transcribed_text = ""
        st.rerun()

with col2:
    st.header("Transcription")

    # Indicateur d'état
    if st.session_state.is_listening:
        if st.session_state.pause_listening:
            st.warning("⏸️ Reconnaissance en pause")
        else:
            st.success("🎤 En écoute...")
    else:
        st.info("⏹️ En attente de démarrage")

    # Zone de texte pour afficher la transcription
    transcription_display = st.text_area(
        "Texte transcrit",
        value=st.session_state.transcribed_text,
        height=400,
        placeholder="Le texte transcrit apparaîtra ici...",
        label_visibility="collapsed"
    )

# Section d'information
with st.expander("ℹ️ Informations et aide"):
    st.markdown("""
    ### Guide d'utilisation:
    1. **Sélectionnez l'API** de reconnaissance vocale que vous souhaitez utiliser
    2. **Choisissez la langue** parlée pour améliorer la précision
    3. **Démarrez l'écoute** et parlez clairement dans votre microphone
    4. **Mettez en pause** si nécessaire, puis **reprenez** l'écoute
    5. **Sauvegardez** votre transcription quand vous le souhaitez

    ### Conseils pour de meilleurs résultats:
    - Parlez clairement et à un rythme modéré
    - Utilisez un microphone de qualité dans un environnement calme
    - Ajustez la sensibilité si nécessaire dans les paramètres avancés
    - Pour les APIs nécessitant une clé, assurez-vous d'avoir un compte actif

    ### APIs supportées:
    - **Google**: Reconnaissance de base, gratuite mais avec des limites
    - **Google Cloud**: Service payant avec une précision améliorée
    - **Sphinx**: Reconnaissance hors ligne (anglais seulement, précision limitée)
    - **Wit.ai**: Service de Facebook, nécessite une clé API
    - **Microsoft Bing**: Service de Microsoft, nécessite une clé API
    - **IBM Speech to Text**: Service IBM Watson, nécessite des identifiants
    """)

# Pied de page
st.markdown("---")
st.markdown("*Application de reconnaissance vocale améliorée avec Streamlit*")