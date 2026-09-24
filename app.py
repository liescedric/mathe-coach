import streamlit as st
from openai import OpenAI
import re

# 1. Seiten-Design
st.set_page_config(page_title="Mathe-Coach", page_icon="🧮", layout="wide")

# 2. Visuelles Design (Schatten entfernt, Rahmen an Streamlit angepasst)
css_start = "<" + "style" + ">"
css_end = "<" + "/style" + ">"
custom_css = css_start + """
@import url('https://fonts.googleapis.com/css2?family=Caveat:wght@500&display=swap');

/* Verstecke die Scrollbar im Notizzettel für eine saubere Optik */
.notizzettel-box::-webkit-scrollbar {
    width: 0px;
    background: transparent;
}

.notizzettel-box {
    background-color: #ffffff;
    background-image: 
        linear-gradient(#e0e0e0 1px, transparent 1px),
        linear-gradient(90deg, #e0e0e0 1px, transparent 1px);
    background-size: 30px 30px; 
    background-position: 0 0;
    padding: 30px 20px 30px 20px; 
    
    /* Streamlit-ähnlicher flacher Rand ohne Schatten */
    border: 1px solid rgba(49, 51, 63, 0.2);
    border-radius: 8px; 
    
    font-family: 'Caveat', cursive;
    font-size: 24px;
    color: #000080;
    
    /* Exakte Höhe, passend zum Chat-Container */
    height: 600px;
    overflow-y: auto;
    
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
    
    st.info("💡 **Tipp:** Lege dir am besten ein Blatt Papier und einen Stift bereit, um nebenbei mitzuschreiben und zu rechnen!")

# 4. API-Key laden
if "GROQ_API_KEY" in st.secrets:
    client = OpenAI(
        api_key=st.secrets["GROQ_API_KEY"],
        base_url="https://api.groq.com/openai/v1"
    )
else:
    st.error("Bitte hinterlege den API-Key (GROQ_API_KEY) in den Streamlit Secrets.")
    st.stop()

# 5. Der System-Prompt
system_prompt = """
Du bist ein professioneller, extrem anpassungsfähiger Mathe-Coach (8. Klasse). 
DEIN ZIEL: Der Schüler erarbeitet den Lösungsweg selbst. Du löst NIEMALS Aufgaben für ihn.

GEHEIMWISSEN (NUR FÜR DICH - VERRATE ES NICHT VORHER!):
- Aufgabe 1: x+y=20, 2x+4y=54
- Aufgabe 2: 3b+2m=6,80; 2b+4m=8,80
- Aufgabe 3: e+s=150, 8e+5s=990

DIDAKTISCHE PRINZIPIEN (WICHTIG!):
1. NON-LINEARES DENKEN: Schüler denken oft chaotisch. Die Schritte "Unbekannte definieren" und "Gleichungen aufstellen" müssen NICHT in einer starren Reihenfolge passieren. Wenn ein Schüler direkt eine Gleichung oder Rechnung in den Raum wirft, bremse ihn nicht aus! Akzeptiere es, lobe ihn und nimm es auf den Notizzettel auf. Greife nur strukturierend ein, wenn der Schüler sich völlig verrennt.
2. ANSCHAULICHE ERKLÄRUNGEN NUR BEI BEDARF: Sei immer bereit, Sachverhalte extrem anschaulich (z.B. mit Beispielen aus dem Alltag) zu erklären. Erkläre etwa, wenn der Schüler explizit fragt ("Ich verstehe das nicht") ODER wenn du in deiner DIAGNOSE ein schwerwiegendes Verständnisproblem feststellst.
3. MINIMALISTISCHE INTERVENTION: Stelle immer nur EINE kurze Gegenfrage. Wenn der Schüler richtig liegt, bestätige kurz und warte.

REGELN FÜR DEN NOTIZZETTEL:
1. Der Notizzettel wächst organisch mit den Gedanken des Schülers.
2. Zeige NUR die Kategorien an, die der Schüler BEREITS erarbeitet hat (z.B. "Gesucht:", "Gegeben (Gleichungen):", "Rechnung:", "Antwortsatz:").
3. Schreibe NIEMALS Platzhalter wie "[Noch nicht erarbeitet],[Sammelteil], [Rechenteil], [Antwortsatz]". Lass unerarbeitete Dinge einfach komplett weg.
4. Trage Erkenntnisse sofort in den Zettel ein, auch wenn sie "in der falschen Reihenfolge" vom Schüler genannt wurden.
5. Keine LaTeX-Zeichen im Notizzettel (keine $, keine Klammern).
6. Schreib ausschließlich!!! nur die Informationen auf den Notizzettel, die der Schüler selbst geschrieben hat.
7. STRUKTUR DES NOTIZZETTELS (STRIKTES TEMPLATE):
Der Notizzettel muss für jede Aufgabe immer in genau drei Abschnitte unterteilt sein. Trenne die Abschnitte mit einer leeren Zeile. Halte den Text minimal. Schreibe die Abschnitte nicht als Platzhalter, die Struktur gilt nur intern für dich.
Nutze exakt dieses Format:

- Sammle hier nur stichpunktartig die definierten Variablen und Gleichungen (z.B. x = Hühner).

- Schreibe hier die Rechnung auf.
- PRO ZEILE genau eine Gleichung.
- Schreibe die Rechenoperation rechts daneben, getrennt durch einen senkrechten Strich (z.B. 2x + 4y = 54   | -2x).
- Unterstreiche Zwischen- und Endergebnisse zwingend mit HTML-Tags (z.B. y = 7).

- Schreibe exakt das Wort "Antwortsatz: " gefolgt von dem Lösungssatz, welche der Schüler gibt.

8. AUFGABEN-BLÖCKE & ZWINGENDE SORTIERUNG (MULTITASKING):
- Sobald der Schüler eine Aufgabe wählt, generierst du als erstes die Überschrift "Aufgabe [1/2/3]" auf dem Notizzettel.
- Alles, was zu dieser Aufgabe gehört, wird streng unter dieser Überschrift strukturiert (nach Regel 7).
- WICHTIG BEIM WECHSELN: Wenn der Schüler eine Aufgabe pausiert und eine andere beginnt, LÖSCHE NICHTS! Behalte alle bisherigen Blöcke.
- FESTE REIHENFOLGE: Die Blöcke auf dem Notizzettel MÜSSEN immer strikt nach Aufgabennummer sortiert sein (von oben nach unten: Aufgabe 1, dann Aufgabe 2, dann Aufgabe 3). 
- BEISPIEL: Auch wenn der Schüler zuerst Aufgabe 3 und danach Aufgabe 1 bearbeitet, muss der neue Block "Aufgabe 1" zwingend GANZ OBEN über "Aufgabe 3" eingefügt werden. Es darf maximal diese 3 Blöcke geben.

FORMAT DEINER ANTWORT:
Deine Ausgabe MUSS zwingend aus diesen drei Teilen bestehen (nutze exakt diese Schlüsselwörter):

DIAGNOSE:
[Notiere hier kurz für dich: Hat der Schüler einen unkonventionellen, aber richtigen Ansatz? Versteht er das Konzept oder braucht er jetzt zwingend eine anschauliche Erklärung, weil er blockiert ist?]

CHAT:
[Deine empathische Antwort an den Schüler. Nutze \(...\) für Mathe im Chat.]

NOTIZZETTEL:
[Hier steht nur das, was bereits erarbeitet wurde. Wachsend und flexibel in der Reihenfolge, je nachdem, was der Schüler geliefert hat.]
"""

# 6. Initialisierung
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]
    
    start_msg = """DIAGNOSE:
Start des Chats. Der Schüler muss sich zunächst für eine Aufgabe entscheiden.
CHAT:
Hallo! Ich bin dein Mathe-Coach. Welche der drei Aufgaben wollen wir uns zuerst ansehen?
NOTIZZETTEL:
Noch leer. Wähle eine Aufgabe, um zu starten!"""
    
    st.session_state.messages.append({"role": "assistant", "content": start_msg})

if "notizzettel" not in st.session_state:
    st.session_state.notizzettel = "Noch leer. Wähle eine Aufgabe, um zu starten!"

# 7. Layout in Spalten aufteilen (angepasst für zentrierteres Design: 1.5 zu 1)
chat_col, note_col = st.columns([1.5, 1])

# Linker Bereich: Chat & Überschrift
with chat_col:
    st.subheader("🧮 Lernen mit Lenny")
    # Chat-Container auf exakt 600px Höhe
    chat_container = st.container(height=600)
    
    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] != "system":
                content = msg["content"]
                
                if msg["role"] == "assistant":
                    chat_match = re.search(r'CHAT:(.*?)(?=NOTIZZETTEL:|$)', content, re.DOTALL)
                    if chat_match:
                        display_text = chat_match.group(1).strip()
                    else:
                        display_text = content
                else:
                    display_text = content
                
                if msg["role"] == "assistant" and "NOTIZZETTEL:" in content:
                    note_match = re.search(r'NOTIZZETTEL:(.*)', content, re.DOTALL)
                    if note_match:
                        st.session_state.notizzettel = note_match.group(1).strip()
                
                with st.chat_message(msg["role"]):
                    st.markdown(display_text)

# Rechter Bereich: Notizzettel & parallele Überschrift
with note_col:
    st.subheader("📄 Notizen")
    box_start = "<" + "div class='notizzettel-box'" + ">"
    box_end = "<" + "/div" + ">"
    st.markdown(box_start + st.session_state.notizzettel + box_end, unsafe_allow_html=True)


# 8. Chat-Eingabe
user_input = st.chat_input("Schreibe hier...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with chat_container:
        with st.chat_message("user"):
            st.markdown(user_input)
        
        with st.chat_message("assistant"):
            try:
                # 120B Modell
                stream = client.chat.completions.create(
                    model="openai/gpt-oss-120b", 
                    messages=st.session_state.messages,
                    stream=False
                )
                full_response = stream.choices[0].message.content
                
                chat_match = re.search(r'CHAT:(.*?)(?=NOTIZZETTEL:|$)', full_response, re.DOTALL)
                if chat_match:
                    display_text = chat_match.group(1).strip()
                else:
                    display_text = full_response
                
                note_match = re.search(r'NOTIZZETTEL:(.*)', full_response, re.DOTALL)
                if note_match:
                    st.session_state.notizzettel = note_match.group(1).strip()
                
                st.markdown(display_text)
                
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
                st.rerun()
                
            except Exception as e:
                st.error(f"Es gab ein Problem: {e}")
