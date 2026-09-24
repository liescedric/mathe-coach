import streamlit as st
from openai import OpenAI
import re

# 1. Seiten-Design
st.set_page_config(page_title="Mathe-Coach", page_icon="🧮", layout="wide")

# 2. Visuelles Design (Nur noch für das Karopapier)
css_start = "<" + "style" + ">"
css_end = "<" + "/style" + ">"
custom_css = css_start + """
@import url('https://fonts.googleapis.com/css2?family=Caveat:wght@500&display=swap');

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
    st.success("Tipp: Der Chat hat jetzt ein eigenes Scrollfenster. Der Zettel bleibt rechts fixiert!")

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

# 5. Der System-Prompt (mit starker Vorgabe zur Antwort-Struktur)
system_prompt = """
Du bist ein exzellenter, adaptiver Mathe-Coach (8. Klasse). DEIN ZIEL: Der Schüler modelliert und rechnet selbstständig. Du löst NIEMALS Aufgaben für ihn.

GEHEIMWISSEN FÜR DICH:
- Aufgabe 1: x+y=20, 2x+4y=54
- Aufgabe 2: 3b+2m=6,80; 2b+4m=8,80
- Aufgabe 3: e+s=150, 8e+5s=990

ADAPTIVE DIAGNOSE & ANTWORTSTRUKTUR (STRIKT EINHALTEN!):
Deine Antwort MUSS zwingend aus drei Teilen bestehen:
1. Eine unsichtbare Diagnose (in kleinen Buchstaben: ...)
2. Die sichtbare Chat-Antwort an den Schüler (Stelle immer nur EINE kurze Gegenfrage! Weigere dich, wenn der Schüler "Löse das" fordert.)
3. Der Notizzettel, eingeleitet mit "NOTIZZETTEL:"

FORMATIERUNG CHAT:
Nutze für Mathematik im Chat IMMER das Format \(x+y=20\). Keine Klammern wie \(x+y=20\)!

FORMATIERUNG NOTIZZETTEL:
Nutze im Notizzettel KEINE LATEX-ZEICHEN (\(,\), \(,\)$). Schreibe reinen Text!
Nutze exakt diese Struktur (nur ausfüllen, was der Schüler schon weiß):
Aufgabe [Nummer]
Gesucht: 
[Unbekannte]
Gegeben: 
[Informationen]
Rechnung:
[Gleichungen]
Lösungssatz: 
[Ergebnis]
"""

# 6. Chat-Verlauf und Notizzettel initialisieren
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]
    start_msg = "\nStart.\n\nHallo! Ich bin dein Mathe-Coach. Welche der drei Aufgaben wollen wir uns zuerst ansehen?\n\nNOTIZZETTEL:\nNoch leer. Wähle eine Aufgabe, um zu starten!"
    st.session_state.messages.append({"role": "assistant", "content": start_msg})

if "notizzettel" not in st.session_state:
    st.session_state.notizzettel = "Noch leer. Wähle eine Aufgabe, um zu starten!"

# 7. Layout in Spalten aufteilen
chat_col, note_col = st.columns([2, 1])

# Rechter Bereich: Notizzettel
with note_col:
    box_start = "<" + "div class='notizzettel-box'" + ">"
    box_end = "<" + "/div" + ">"
    st.markdown("### 📄 Dein Notizzettel")
    st.markdown(box_start + st.session_state.notizzettel + box_end, unsafe_allow_html=True)

# Linker Bereich: Chat (JETZT IN EINEM EIGENEN SCROLL-CONTAINER)
with chat_col:
    # Dieser Container sorgt dafür, dass nur der Chat scrollt (600px Höhe)
    chat_container = st.container(height=600)
    
    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] != "system":
                # Notizzettel abtrennen
                content = msg["content"].split("NOTIZZETTEL:")[0].strip()
                
                # Diagnose herausfiltern (robuster gemacht mit re.IGNORECASE)
                display_text = re.sub(r".*?", "", content, flags=re.DOTALL | re.IGNORECASE).strip()
                
                # Fallback, falls die KI die Antwort verbockt hat und der Text leer ist
                if not display_text:
                    display_text = content 
                
                with st.chat_message(msg["role"]):
                    st.markdown(display_text)

# 8. Chat-Eingabe
user_input = st.chat_input("Schreibe hier...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with chat_container:
        with st.chat_message("user"):
            st.markdown(user_input)
        
        with st.chat_message("assistant"):
            try:
                # Wir verwenden das 120B Modell
                stream = client.chat.completions.create(
                    model="openai/gpt-oss-120b", 
                    messages=st.session_state.messages,
                    stream=False
                )
                full_response = stream.choices[0].message.content
                
                # Extrahieren des Notizzettels
                if "NOTIZZETTEL:" in full_response:
                    chat_text, notizzettel_text = full_response.split("NOTIZZETTEL:", 1)
                    st.session_state.notizzettel = notizzettel_text.strip()
                else:
                    chat_text = full_response
                
                # Extrahieren der Chat-Nachricht
                display_text = re.sub(r".*?", "", chat_text, flags=re.DOTALL | re.IGNORECASE).strip()
                if not display_text:
                    display_text = chat_text # Fallback, falls was schiefgeht
                
                st.markdown(display_text)
                
                # Wir speichern die VOLLSTÄNDIGE Antwort im Verlauf
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
                st.rerun()
                
            except Exception as e:
                st.error(f"Es gab ein Problem: {e}")
