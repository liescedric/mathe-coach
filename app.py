import streamlit as st
from openai import OpenAI

# 1. Seiten-Design
st.set_page_config(page_title="Mathe-Coach", page_icon="🧮", layout="wide")

# 2. Visuelles Design (Perfekt ausgerichtetes Karopapier & Sticky Wrapper)
css_start = "<" + "style" + ">"
css_end = "<" + "/style" + ">"
custom_css = css_start + """
@import url('https://fonts.googleapis.com/css2?family=Caveat:wght@500&display=swap');

/* Der Wrapper, der den Zettel beim Scrollen festhält */
.sticky-wrapper {
    position: -webkit-sticky;
    position: sticky;
    top: 2rem;
    z-index: 100;
}

/* Der Notizzettel mit exakt synchronisierten Linien */
.notizzettel-box {
    background-color: #ffffff;
    background-image: 
        linear-gradient(#e0e0e0 1px, transparent 1px),
        linear-gradient(90deg, #e0e0e0 1px, transparent 1px);
    background-size: 30px 30px; 
    background-position: 0 0;
    padding: 30px 20px 30px 20px; 
    border: 1px solid #ccc;
    border-radius: 5px;
    font-family: 'Caveat', cursive;
    font-size: 24px;
    color: #000080;
    min-height: 500px;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    white-space: pre-wrap;
    line-height: 30px; 
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
    Für ein Schulkonzert wurden 150 Karten verkauft. Erwachsene kosten 8 Euro, Schüler 5 Euro. Einnahmen 990 Euro.
    *Frage: Wie viele Erwachsene und wie viele Schüler waren auf dem Konzert?*
    """)
    st.success("Tipp: Der Notizzettel rechts scrollt immer mit und bleibt im Blick!")

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

# 5. Der extrem verschärfte System-Prompt
system_prompt = """
Du bist ein Mathe-Coach (8. Klasse). DEIN ZIEL IST ES, DASS DER SCHÜLER SELBST RECHNET. DU LÖST NIEMALS AUFGABEN!

DEIN GEHEIMWISSEN (Niemals verraten, bevor der Schüler es nicht selbst gesagt hat!):
- Aufgabe 1: x+y=20, 2x+4y=54
- Aufgabe 2: Brezeln (b) und Muffins (m). 3b+2m=6,80; 2b+4m=8,80
- Aufgabe 3: Erwachsene (e) und Schüler (s). e+s=150, 8e+5s=990

STRIKTE VERHALTENSREGELN (Zwingend einhalten!):
1. RECHENVERBOT: Wenn der Schüler "lösen bitte", "rechne das" oder ähnliches fordert, WEIGERE DICH FREUNDLICH. Sage: "Ich bin dein Coach, ich rechne nicht für dich. Was wäre dein erster eigener Schritt?"
2. KEINE HALLUZINATIONEN: Bleibe exakt bei den Aufgaben (b ist Brezel, niemals Banane! e sind Erwachsene, keine eiskalten Tickets!).
3. EINE FRAGE: Stelle in deiner Antwort immer nur EINE einzige Gegenfrage.
4. PASSIVITÄT: Wenn der Schüler richtig rechnet, sage nur "Stimmt!" und warte auf seinen nächsten Schritt.

FORMATIERUNG:
1. Nutze im Chat für Mathematik IMMER ein Dollar-Zeichen (z.B. \(x+y=20\)).
2. VERBOTEN: Eckige Klammern [...] oder Konstrukte wie \\qquad sind absolut verboten!

REGELN FÜR DEN NOTIZZETTEL:
1. Schreibe am Ende JEDER deiner Antworten: "NOTIZZETTEL:" gefolgt vom aktuellen Wissen.
2. Der Notizzettel ist zu Beginn komplett LEER. Schreibe dein Geheimwissen NICHT dorthin!
3. Füge Variablen und Gleichungen ERST DANN in den Notizzettel ein, WENN der Schüler sie im Chat richtig aufgestellt hat.
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
    wrap_start = "<" + "div class='sticky-wrapper'" + ">"
    box_start = "<" + "div class='notizzettel-box'" + ">"
    box_end = "<" + "/div" + ">"
    wrap_end = "<" + "/div" + ">"
    
    st.markdown("### 📄 Dein Notizzettel")
    st.markdown(wrap_start + box_start + st.session_state.notizzettel + box_end + wrap_end, unsafe_allow_html=True)

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
