import streamlit as st
import streamlit.components.v1 as components

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

st.subheader("📝 Transcription en direct")

# --- On va afficher la transcription dans un iframe HTML (JS met à jour la valeur) ---
components.html(f"""
<textarea id="transcription" style="width:100%; height:200px;" placeholder="La transcription apparaîtra ici..."></textarea>
<script>
var recognition;
function startRecognition() {{
    if (!('webkitSpeechRecognition' in window)) {{
        alert("Votre navigateur ne supporte pas la reconnaissance vocale. Utilisez Chrome ou Edge.");
        return;
    }}
    recognition = new webkitSpeechRecognition();
    recognition.lang = "{lang_code}";
    recognition.continuous = true;
    recognition.interimResults = true;

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

startRecognition();
</script>
""", height=250)

# Bouton pour récupérer et sauvegarder le texte
if st.button("💾 Enregistrer transcription.txt"):
    # On ne peut pas récupérer directement la valeur du textarea du JS,
    # mais l'utilisateur peut copier/coller dans Streamlit, ou on utilise un composant bidirectionnel plus avancé.
    st.warning("Pour sauvegarder, sélectionnez et copiez le texte du textarea ci-dessus.")
