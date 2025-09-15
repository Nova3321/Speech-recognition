import streamlit as st
import streamlit.components.v1 as components
import os

st.set_page_config(page_title="Reconnaissance vocale Live", layout="centered")
st.title("🎤 Reconnaissance vocale live (Web Speech API)")

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
st.subheader("📝 Transcription")
if "transcription" not in st.session_state:
    st.session_state.transcription = ""

transcription_placeholder = st.empty()
transcription_placeholder.text_area("Texte transcrit :", value=st.session_state.transcription, height=200)

# --- Composant JavaScript pour transcription live ---
js_code = f"""
<script>
var finalTranscript = "";
var recognizing = false;

function startRecognition() {{
    if (!('webkitSpeechRecognition' in window)) {{
        alert("Votre navigateur ne supporte pas la reconnaissance vocale. Utilisez Chrome ou Edge.");
        return;
    }}

    var recognition = new webkitSpeechRecognition();
    recognition.lang = '{lang_code}';
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onstart = function() {{
        recognizing = true;
        console.log("🎙️ Reconnaissance vocale démarrée...");
    }};

    recognition.onerror = function(event) {{
        console.log("Erreur reconnaissance vocale:", event.error);
    }};

    recognition.onend = function() {{
        recognizing = false;
        console.log("🔴 Reconnaissance vocale terminée.");
    }};

    recognition.onresult = function(event) {{
        var interimTranscript = "";
        for (var i = event.resultIndex; i < event.results.length; ++i) {{
            if (event.results[i].isFinal) {{
                finalTranscript += event.results[i][0].transcript + " ";
            }} else {{
                interimTranscript += event.results[i][0].transcript;
            }}
        }}
        // Envoyer au Streamlit
        window.parent.postMessage({{type:'update_transcription', text: finalTranscript + interimTranscript}}, "*");
    }};

    recognition.start();
}}

// Démarrer la reconnaissance dès que la page est chargée
startRecognition();
</script>
"""

# Injecter le JS
components.html(js_code, height=0, width=0)

# Recevoir la transcription du JS
# On utilise un petit hack avec st.experimental_get_query_params
if "transcription" not in st.session_state:
    st.session_state.transcription = ""

# Bouton pour sauvegarder
if st.button("💾 Enregistrer dans transcription.txt"):
    with open("transcription.txt", "a", encoding="utf-8") as f:
        f.write(st.session_state.transcription + "\n")
    st.success("Texte enregistré dans transcription.txt")
