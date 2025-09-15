# app.py
import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import speech_recognition as sr
import numpy as np
import io
import wave
import time

st.set_page_config(page_title="Reconnaissance Vocale (WebRTC)", layout="centered")

LANGUAGES = {
    "Français": "fr-FR",
    "Anglais": "en-US",
    "Espagnol": "es-ES",
    "Arabe": "ar-SA",
}

st.title("🎤 Reconnaissance vocale (WebRTC)")

lang_choice = st.selectbox("Choisissez la langue :", list(LANGUAGES.keys()))
lang_code = LANGUAGES[lang_choice]

if "transcription" not in st.session_state:
    st.session_state.transcription = ""

st.info("Autorise l'accès au micro dans ton navigateur (popup). Utilise Chrome/Edge pour de meilleurs résultats.")

# Démarre la session WebRTC (envoi audio uniquement)
webrtc_ctx = webrtc_streamer(
    key="speech",
    mode=WebRtcMode.SENDONLY,
    media_stream_constraints={"audio": True, "video": False},
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
)

def frames_to_wav_bytes(frames):
    """
    Convertit une liste d'av.AudioFrame en bytes WAV mono 16-bit.
    """
    if not frames:
        return None

    # Récupérer sample_rate depuis la première frame
    sample_rate = frames[0].sample_rate

    # Convertir chaque frame en ndarray et concaténer
    arrays = [f.to_ndarray() for f in frames]
    arr = np.concatenate(arrays, axis=0)

    # Si multi-canal -> convertir en mono en faisant la moyenne
    if arr.ndim > 1:
        arr = arr.mean(axis=1)

    # Si float (-1..1), convertir en int16
    if np.issubdtype(arr.dtype, np.floating):
        arr = (arr * 32767).astype(np.int16)
    else:
        arr = arr.astype(np.int16)

    # Écrire en WAV dans un buffer
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 2 bytes = 16 bits
        wf.setframerate(sample_rate)
        wf.writeframes(arr.tobytes())
    buf.seek(0)
    return buf

st.markdown("---")
st.write("⚙️ Paramètres de capture")
duration = st.slider("Durée (secondes) à récupérer pour la transcription :", 1, 10, 3)

col1, col2 = st.columns(2)
with col1:
    transcribe_btn = st.button("🔴 Transcrire maintenant")
with col2:
    clear_btn = st.button("🧹 Effacer la transcription affichée")

if clear_btn:
    st.session_state.transcription = ""
    st.success("Transcription effacée.")

if transcribe_btn:
    if webrtc_ctx is None:
        st.error("webrtc non initialisé.")
    elif webrtc_ctx.state.playing is False:
        st.warning("Le micro n'est pas actif. Vérifie la permission du navigateur.")
    elif webrtc_ctx.audio_receiver is None:
        st.error("Récepteur audio non disponible.")
    else:
        st.info("Collecte des frames audio... parle maintenant.")
        frames = []
        t_end = time.time() + duration
        # Récupère les frames pendant `duration` secondes
        while time.time() < t_end:
            try:
                new_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
                if new_frames:
                    frames.extend(new_frames)
            except Exception:
                # timeout ou pas de frames ; on continue
                pass

        if not frames:
            st.warning("Aucune donnée audio reçue : vérifie que le micro est autorisé et que tu parles.")
        else:
            st.info(f"{len(frames)} frames reçues — conversion en WAV...")
            wav_buf = frames_to_wav_bytes(frames)
            if wav_buf is None:
                st.error("Erreur lors de la conversion audio.")
            else:
                r = sr.Recognizer()
                try:
                    with sr.AudioFile(wav_buf) as source:
                        audio = r.record(source)
                        st.info("Envoi à l'API de reconnaissance (Google)...")
                        # Appel Google (gratuit mais limité). Tu peux remplacer / ajouter d'autres services si tu veux.
                        text = r.recognize_google(audio, language=lang_code)
                        st.session_state.transcription += text + " "
                        st.success("Transcription réussie ✅")
                except sr.UnknownValueError:
                    st.error("❌ Google n'a pas compris l'audio.")
                except sr.RequestError as e:
                    st.error(f"⚠️ Erreur requête API Google : {e}")
                except Exception as e:
                    st.error(f"Erreur inattendue lors de la transcription : {e}")

st.markdown("---")
st.subheader("📝 Transcription (accumulée)")
st.write(st.session_state.transcription)

if st.button("💾 Enregistrer dans transcription.txt"):
    with open("transcription.txt", "a", encoding="utf-8") as f:
        f.write(st.session_state.transcription + "\n")
    st.success("Texte enregistré dans transcription.txt")

import librosa

def frames_to_wav_bytes(frames):
    if not frames:
        return None

    sample_rate = frames[0].sample_rate
    arrays = [f.to_ndarray() for f in frames]
    arr = np.concatenate(arrays, axis=0)

    if arr.ndim > 1:
        arr = arr.mean(axis=1)

    if np.issubdtype(arr.dtype, np.floating):
        arr = (arr * 32767).astype(np.int16)
    else:
        arr = arr.astype(np.int16)

    # 🔥 Conversion explicite vers 16000 Hz
    arr_16k = librosa.resample(arr.astype(np.float32), orig_sr=sample_rate, target_sr=16000)
    arr_16k = (arr_16k * 32767).astype(np.int16)

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)   # <- imposé
        wf.writeframes(arr_16k.tobytes())
    buf.seek(0)
    return buf
