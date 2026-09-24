import streamlit as st
from openai import OpenAI

# 1. Seiten-Design
st.set_page_config(page_title="Mathe-Coach", page_icon="🧮", layout="wide")

# 2. Visuelles Design (Kariertes Papier, Handschrift & Sticky Notizzettel)
css_start = "<" + "style" + ">"
css_end = "<" + "/style" + ">"
custom_css = css_start + """
@import url('https://fonts.googleapis.com/css2?family=Caveat:wght@500&display=swap');

/* Mache die rechte Spalte (Notizzettel) klebrig beim Scrollen */
[data-testid="column"]:nth-of-type(2) {
    position: -webkit-sticky;
    position: sticky;
    top: 4rem;
    align-self: flex-start;
    z-index: 10;
}

.notizzettel-box {
    background-color: #ffffff;
    background-image: 
        linear-gradient(#d9d9d9 1px, transparent 1px),
        linear-gradient(90deg, #d9d9d9 1px, transparent 1px);
    background-size: 20px 20px;
    padding: 20px 20px 40px 20px;
    border: 1px solid #ccc;
    border-radius: 5px;
    font-family: 'Caveat', cursive;
    font-size: 26px;
    color: #000080;
    min-height: 400px;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    white-space: pre-wrap;
    line-height: 1.5;
}
""" + css_end
st.markdown(custom_css, unsafe_allow_html=True)

# 3. ÜBERSICHT IN DER LINKEN SEITENLEISTE
with st.sidebar:
    st.title("📝 Deine Aufgaben")
    st.markdown("""
    **Aufgabe 1: Hühner & Schweine**
    Auf einem Bauernhof gibt es Hühner und Schweine. Insgesamt sind es 20 Tiere. Zusammen haben sie 54 Beine. 
    *Frage: Wie viele Hühner und wie viele Schweine sind es?*
    
    **Aufgabe 2: Cafeteria**
    Anna kauft 3 Brezeln und 2 Muffins für 6,80 Euro. Ben kauft 2 Brezeln und 4 Muffins für 8,80 Euro. 
    *Frage: Wie viel kostet eine Brezel und wie viel ein Muffin?*
    
    **Aufgabe 3: Konzertkarten**
    Für ein Schulkonzert wurden 150 Karten verkauft. Erwachsene 8 Euro, Schüler 5 Euro. Einnahmen 990 Euro.
    *Frage: Wie viele Erwachsene und wie viele Schüler waren auf dem Konzert?*
    """)
    st.success("Tipp: Der Chat ist links. Dein Notizzettel rechts scrollt jetzt immer mit!")

st.title("🧮 Dein interaktiver Mathe-Coach")

# 4. API-Key laden
if "GROQ_API_KEY" in st.secrets:
    client = OpenAI(
        api_key=st.secrets["GROQ_API_KEY"],
        base_url="https://api.groq.com/openai/v1"
    )
else:
    st.error("Bitte hinterlege den API-Key (GROQ_API_KEY) in den Streamlit Secrets.")
    st.stop()

# 5. Der System-Prompt (Fokus: Sokratischer Dialog & Empathie)
system_prompt = """
Du bist ein empathischer, sokratischer Mathe-Tutor (8. Klasse). Du löst keine Aufgaben, sondern befähigst den Schüler, selbst zu denken.

Geheimwissen für dich:
1. Hühner & Schweine: Hühner = 2 Beine, Schweine = 4 Beine. (x+y=20, 2x+4y=54)
2. Cafeteria: 3 Brezeln + 2 Muffins = 6,80 Euro; 2 Brezeln + 4 Muffins = 8,80 Euro
3. Konzertkarten: e+s=150, 8e+5s=990

STRIKTE DIDAKTIK-REGELN (WICHTIG!):
1. EMPATHIE & GRUNDLAGEN ZUERST: Wenn der Schüler Verständnisfragen stellt (z.B. "Was ist ein x?", "Was ist eine Gleichung?", "Ich verstehe das nicht"), STOPPE das Rechnen sofort. Erkläre das Konzept sehr einfach und alltagsnah, bevor ihr mit der Aufgabe weitermacht.
2. SOKRATISCHER DIALOG: Zwinge dem Schüler niemals deinen Lösungsweg auf. Wenn die Gleichungen stehen, frage: "Kennst du ein Verfahren, um solche Gleichungen zu lösen?". Lass ihn wählen (Einsetzungs-, Gleichsetzungs- oder Additionsverfahren). 
3. STRUKTURIERTE PHASEN: Behandle jede Aufgabe in dieser Reihenfolge:
   - Phase 1: Unbekannte definieren (Was suchen wir?)
   - Phase 2: Gleichungen aufstellen (Modellieren)
   - Phase 3: Lösungsverfahren wählen
   - Phase 4: Schrittweise rechnen
   Springe niemals direkt zu Phase 3, wenn Phase 2 nicht abgeschlossen ist.
4. ZURÜCKHALTUNG: Wenn der Schüler einen richtigen Schritt macht, bestätige es kurz ("Stimmt!") und WARTE. Frag nicht ständig "Was machen wir jetzt?", lass ihm Zeit nachzudenken. Gib nur Hilfestellung, wenn er stecken bleibt.

STRIKTE FORMATIERUNGS-REGELN:
1. Nutze im Chat für Mathematik AUSNAHMSLOS das Dollar-Zeichen-Format. Schreibe IMMER \(x+y=20\). 
2. VERBOTEN: Normale Klammern als Mathe-Ersatz wie (x+y=20) oder \(((x))\) sind strengstens verboten!
3. Am Ende JEDER deiner Antworten schreibst du zwingend das Wort "NOTIZZETTEL:" gefolgt von den aktuell gültigen Gleichungen oder Variablen. Schreibe hier NUR Dinge auf, die ihr bereits klar vereinbart habt.
4. Für den Notizzettel nutze reinen Text (ohne Markdown/Dollarzeichen), z.B. 2x + 4y = 54.
"""

# 6. Chat-Verlauf und Notizzettel initialisieren
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]
    start_msg = "Hallo! Ich bin dein Mathe-Coach. Welche der drei Aufgaben wollen wir uns zuerst ansehen?"
    st.session_state.messages.append({"role": "assistant", "content": start_msg})

if "notizzettel" not in st.session_state:
    st.session_state.notizzettel = "Noch leer. Wir fangen gerade erst an!"

# 7. Layout in Spalten aufteilen
chat_col, note_col = st.columns([2, 1])

# Rechter Bereich: Notizzettel
with note_col:
    # Den Expander weglassen, damit das Sticky-Verhalten besser funktioniert
    html_start = "<" + "div class='notizzettel-box'" + ">"
    html_end = "<" + "/div" + ">"
    st.markdown("### 📄 Dein Notizzettel")
    st.markdown(html_start + st.session_state.notizzettel + html_end, unsafe_allow_html=True)

# Linker Bereich: Chat
with chat_col:
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            display_text = msg["content"].split("NOTIZZETTEL:")[0].strip()
            with st.chat_message(msg["role"]):
                st.markdown(display_text)

# 8. Chat-Eingabe
user_input = st.chat_input("Schreibe hier...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with chat_col:
        with st.chat_message("user"):
            st.markdown(user_input)
        
        with st.chat_message("assistant"):
            try:
                stream = client.chat.completions.create(
                    model="openai/gpt-oss-20b", 
                    messages=st.session_state.messages,
                    stream=False
                )
                full_response = stream.choices[0].message.content
                
                if "NOTIZZETTEL:" in full_response:
                    chat_text, notizzettel_text = full_response.split("NOTIZZETTEL:")
                    st.session_state.notizzettel = notizzettel_text.strip()
                else:
                    chat_text = full_response
                
                st.markdown(chat_text.strip())
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
                st.rerun()
                
            except Exception as e:
                st.error(f"Es gab ein Problem: {e}")
