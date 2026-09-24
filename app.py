import streamlit as st
from openai import OpenAI

# 1. Seiten-Design
st.set_page_config(page_title="Mathe-Coach", page_icon="🧮", layout="wide")

# 2. Visuelles Design für den Notizzettel (Kariertes Papier & Handschrift)
css_start = "<" + "style" + ">"
css_end = "<" + "/style" + ">"
custom_css = css_start + """
@import url('https://fonts.googleapis.com/css2?family=Caveat:wght@500&display=swap');

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
    st.success("Tipp: Der Chat ist links, dein Notizzettel rechts!")

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

# 5. Der System-Prompt
system_prompt = """
Du bist ein authentischer, sehr zurückhaltender Mathe-Tutor (8. Klasse). Du begleitest den Schüler, aber du drängst ihn nicht und überlässt ihm die Führung.

Geheimwissen für dich (Kontext):
1. Hühner & Schweine: Hühner = 2 Beine, Schweine = 4 Beine. (x+y=20, 2x+4y=54)
2. Cafeteria: 3 Brezeln + 2 Muffins = 6,80 Euro; 2 Brezeln + 4 Muffins = 8,80 Euro
3. Konzertkarten: e+s=150, 8e+5s=990

STRIKTE DIDAKTIK-REGELN (WICHTIG!):
1. ABSOLUTE ZURÜCKHALTUNG: Sei passiv! Wenn der Schüler eine richtige Gleichung, Variable oder Rechnung nennt, lobe ihn kurz (z.B. "Stimmt genau!" oder "Richtig."). WARTE DANN EINFACH AB. Frage NICHT: "Was möchtest du als nächstes tun?" oder "Sollen wir jetzt x auflösen?". Lass den Schüler selbst überlegen, was der nächste Schritt ist.
2. HILFE NUR BEI BEDARF: Greife nur helfend ein, wenn der Schüler einen Fehler macht, eine falsche Fährte verfolgt oder explizit "Ich weiß nicht" sagt. Gib dann nur einen winzigen Denkanstoß.
3. FLEXIBLE VARIABLEN: Akzeptiere JEDE Variablen-Zuweisung des Schülers (z.B. m=Brezel).
4. FREIE WAHL: Lass den Schüler entscheiden, welche Aufgabe er bearbeiten will.

STRIKTE FORMATIERUNGS-REGELN:
1. Nutze im Chat für Formeln IMMER das korrekte Markdown-Math-Format (mit Dollar-Zeichen).
2. VERBOTEN: Nutze NIEMALS normale Klammern um mathematische Ausdrücke.
3. Am Ende JEDER deiner Antworten schreibst du zwingend das Wort "NOTIZZETTEL:" gefolgt von den aktuell gültigen Gleichungen oder Variablen, die ihr bisher gemeinsam erarbeitet habt.
4. WICHTIG FÜR DEN NOTIZZETTEL: Nutze nach dem Wort NOTIZZETTEL KEINE Markdown-Formatierungen, keine Dollar-Zeichen und kein LaTeX. Schreibe die Gleichungen dort als reinen Text (z.B. 3m + 2b = 6,80), damit die Handschrift-Schriftart sie gut darstellen kann.
"""

# 6. Chat-Verlauf und Notizzettel initialisieren
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]
    start_msg = "Hallo! Ich bin dein Mathe-Coach. Mit welcher Aufgabe möchtest du beginnen?"
    st.session_state.messages.append({"role": "assistant", "content": start_msg})

if "notizzettel" not in st.session_state:
    st.session_state.notizzettel = "Noch leer. Wir fangen gerade erst an!"

# 7. Layout in Spalten aufteilen
chat_col, note_col = st.columns([2, 1])

# Rechter Bereich: Notizzettel
with note_col:
    with st.expander("📄 Dein Notizzettel", expanded=True):
        html_start = "<" + "div class='notizzettel-box'" + ">"
        html_end = "<" + "/div" + ">"
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
