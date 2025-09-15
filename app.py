import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime

st.set_page_config(page_title="Reconnaissance vocale Live", layout="centered")
st.title("🎤 Reconnaissance vocale Live (Web Speech API)")

# Choix de la langue
LANGUAGES = {
    "Français": "fr-FR",
    "Anglais": "en-US",
    "Espagnol": "es-ES",
    "Arabe": "ar-SA"
}
lang_choice = st.selectbox("Choisissez la langue :", list(LANGUAGES.keys()))
lang_code = LANGUAGES[lang_choice]

# Zone de transcription
if "transcription" not in st.session_state:
    st.session_state.transcription = ""

components.html(f"""
<div>
<p><b>Status:</b> <span id="status">🟢 Actif</span></p>
<textarea id="transcription" style="width:100%; height:200px;" readonly placeholder="La transcription apparaîtra ici..."></textarea>
<br>
<button onclick="copyText()">📋 Copier dans le presse-papiers</button>
<button onclick="clearText()">🧹 Effacer la transcription</button>
<button onclick="pauseRecognition()">⏸️ Pause</button>
<button onclick="resumeRecognition()">▶️ Reprendre</button>
</div>

<script>
var recognition;
var recognizing = false;
var statusEl = document.getElementById("status");

function startRecognition() {{
    if (!('webkitSpeechRecognition' in window)) {{
        alert("Votre navigateur ne supporte pas la reconnaissance vocale. Utilisez Chrome ou Edge.");
        statusEl.textContent = "🔴 Non supporté";
        return;
    }}

    recognition = new webkitSpeechRecognition();
    recognition.lang = "{lang_code}";
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onstart = function() {{
        recognizing = true;
        statusEl.textContent = "🟢 Actif";
    }};

    recognition.onerror = function(event) {{
        console.log("Erreur reconnaissance vocale:", event.error);
        statusEl.textContent = "⚠️ Erreur";
    }};

    recognition.onend = function() {{
        recognizing = false;
        statusEl.textContent = "🟠 En pause";
    }};

    recognition.onresult = function(event) {{
        var finalTranscript = "";
        for (var i = event.resultIndex; i < event.results.length; ++i) {{
            if (event.results[i].isFinal) {{
                finalTranscript += event.results[i][0].transcript + " ";
            }} else {{
                finalTranscript += event.results[i][0].transcript;
            }}
        }}
        document.getElementById("transcription").value = finalTranscript;
    }};

    recognition.start();
}}

function copyText() {{
    var copyText = document.getElementById("transcription");
    copyText.select();
    copyText.setSelectionRange(0, 99999);
    document.execCommand("copy");
    alert("✅ Transcription copiée !");
}}

function clearText() {{
    document.getElementById("transcription").value = "";
}}

function pauseRecognition() {{
    if (recognition) {{
        recognition.stop();
        statusEl.textContent = "⏸️ En pause";
    }}
}}

function resumeRecognition() {{
    if (recognition && !recognizing) {{
        recognition.start();
        statusEl.textContent = "▶️ Reprise";
    }}
}}

startRecognition();
</script>
""", height=350)

# Sauvegarde côté Streamlit
if st.button("💾 Sauvegarder transcription"):
    st.warning("Pour sauvegarder, sélectionnez et copiez le texte du textarea ci-dessus.")
