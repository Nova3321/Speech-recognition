import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import numpy as np
import av
import io
import wave
import time
import speech_recognition as sr
from scipy.signal import resample

st.set_page_config(page_title="Reconnaissance Vocale WebRTC", layout="centered")

# --- Config langues ---
LANGUAGES = {
    "Français": "fr-FR",
    "Anglais": "en-US",
    "Espagnol": "es-ES",
    "Arabe": "ar-SA"
}

st.title("🎤 Reconnaissance Vocale WebRTC")
st.write("Autorisez le micro, parle et clique sur 'Transcrire' après avoir parlé.")

lang_choice = st.selectbox("Choisissez la langue :", list(LANGUAGES.keys()))
lang_code = LANGUAGES[lang_choice]

if "transcription" not in st.session_state:
    st.session_state.transcription = ""

# --- Lancer WebRTC ---
webrtc_ctx = webrtc_streamer(
    key="speech",
    mode=WebRtcMode.SENDONLY,
    media_stream_constraints={"audio": True, "video": False},
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
)

# --- Durée de capture ---
duration = st.slider("Durée d'enregistrement pour la transcription (secondes) :", 3, 10, 5)

# --- Boutons ---
col1, col2 = st.columns(2)
with col1:
    transcribe_btn = st.button("🔴 Transcrire maintenant")
with col2:
    clear_btn = st.button("🧹 Effacer transcription")

if clear_btn:
    st.session_state.transcription = ""
    st.success("Transcription effacée.")

# --- Fonction conversion frames en WAV 16kHz mono ---
def frames_to_wav_bytes(frames):
    if not frames:
        return None

    sample_rate = frames[0].sample_rate
    arrays = [f.to_ndarray() for f in frames]
    arr = np.concatenate(arrays, axis=0)

    if arr.ndim > 1:
        arr = arr.mean(axis=1)

    # convertir en float32 si nécessaire
    if np.issubdtype(arr.dtype, np.floating):
        arr = (arr * 32767).astype(np.int16)
    else:
        arr = arr.astype(np.int16)

    # resample vers 16000 Hz
    target_rate = 16000
    num_samples = int(len(arr) * target_rate / sample_rate)
    arr_16k = resample(arr, num_samples)

    # normaliser volume
    arr_16k = arr_16k / np.max(np.abs(arr_16k)) * 32767
    arr_16k = arr_16k.astype(np.int16)

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(target_rate)
        wf.writeframes(arr_16k.tobytes())
    buf.seek(0)
    return buf

# --- Transcrire ---
if transcribe_btn:
    if webrtc_ctx.audio_receiver is None:
        st.warning("Le micro n'est pas prêt ou non autorisé.")
    else:
        st.info("Collecte des frames audio... parle maintenant.")
        frames = []
        t_end = time.time() + duration
        while time.time() < t_end:
            try:
                new_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
                if new_frames:
                    frames.extend(new_frames)
            except Exception:
                pass

        if not frames:
            st.warning("Aucune audio capturée. Vérifie le micro et autorisation navigateur.")
        else:
            st.info(f"{len(frames)} frames reçues, conversion en WAV...")
            wav_buf = frames_to_wav_bytes(frames)
            if wav_buf is None:
                st.error("Erreur conversion audio.")
            else:
                # Pour debug : sauvegarder WAV
                # with open("debug.wav", "wb") as f:
                #     f.write(wav_buf.read())
                r = sr.Recognizer()
                try:
                    with sr.AudioFile(wav_buf) as source:
                        audio = r.record(source)
                        st.info("Envoi à l'API Google Speech...")
                        text = r.recognize_google(audio, language=lang_code)
                        st.session_state.transcription += text + " "
                        st.success("✅ Transcription réussie")
                except sr.UnknownValueError:
                    st.error("❌ Google n'a pas compris l'audio.")
                except sr.RequestError as e:
                    st.error(f"⚠️ Erreur requête API Google : {e}")
                except Exception as e:
                    st.error(f"Erreur inattendue : {e}")

st.markdown("---")
st.subheader("📝 Transcription accumulée")
st.write(st.session_state.transcription)

if st.button("💾 Enregistrer transcription.txt"):
    with open("transcription.txt", "a", encoding="utf-8") as f:
        f.write(st.session_state.transcription + "\n")
    st.success("Texte enregistré dans transcription.txt")
