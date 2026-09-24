import streamlit as st
from openai import OpenAI

# 1. Seiten-Design (mit Layout "wide" für mehr Platz)
st.set_page_config(page_title="Mathe-Coach", page_icon="🧮", layout="wide")

# 2. PERMANENTE ÜBERSICHT IN DER SEITENLEISTE (Sidebar)
with st.sidebar:
    st.title("📝 Deine Aufgaben")
    st.markdown("""
    **Aufgabe 1: Hühner & Schweine**
    Auf einem Bauernhof gibt es Hühner und Schweine. Insgesamt sind es 20 Tiere. Zusammen haben sie 54 Beine.
    
    **Aufgabe 2: Cafeteria**
    Anna kauft 3 Brezeln und 2 Muffins für 6,80€. Ben kauft 2 Brezeln und 4 Muffins für 8,80€. 
    
    **Aufgabe 3: Konzertkarten**
    Für ein Schulkonzert wurden 150 Karten verkauft. Erwachsene 8€, Schüler 5€. Einnahmen 990€.
    """)
    st.success("Tipp: Rechne gerne parallel auf einem Blatt Papier mit!")

st.title("🧮 Dein interaktiver Mathe-Coach")

# 3. API-Key laden (Groq über OpenAI-Bibliothek)
if "GROQ_API_KEY" in st.secrets:
    client = OpenAI(
        api_key=st.secrets["GROQ_API_KEY"],
        base_url="https://api.groq.com/openai/v1"
    )
else:
    st.error("Bitte hinterlege den API-Key (GROQ_API_KEY) in den Streamlit Secrets.")
    st.stop()

# 4. Der optimierte System-Prompt
system_prompt = """
Du bist ein motivierender, didaktisch geschulter Lerncoach für Mathematik (8. Klasse).
Dein Ziel: Schüler durch gezieltes Nachfragen (Scaffolding) zur Lösung von linearen Gleichungssystemen führen.

Die Lösungen (NUR FÜR DICH!):
1. Hühner (x) & Schweine (y): x+y=20, 2x+4y=54. (Lösung: 13 Hühner, 7 Schweine).
2. Cafeteria: 3b+2m=6,80, 2b+4m=8,80. (Lösung: Brezel 1,20€, Muffin 1,60€).
3. Konzertkarten: e+s=150, 8e+5s=990. (Lösung: 80 Erw., 70 Schüler).

STRIKTE REGELN ZUM VERHALTEN:
1. Kurze Antworten: Fasse dich kurz. Schreibe keine Romane.
2. Keine Meta-Sprache: Erwähne NIEMALS Wörter wie "Stufe 1", "Methodische Hilfe" oder "Scaffolding" gegenüber dem Schüler. Sprich ganz natürlich, als wärst du ein Nachhilfelehrer.
3. Umgang mit "Ich weiß nicht": Wenn der Schüler nicht weiterweiß, gib einen Tipp. Wenn der Schüler mehrfach (zwei- bis dreimal) hintereinander "ich weiß nicht" sagt oder völlig feststeckt, zeige ihm die Lösung für diesen EINEN Teilschritt auf und stelle direkt die Frage für den nächsten Schritt.
4. Mathe-Formatierung (LaTeX): Nutze für Variablen, Gleichungen und Brüche IMMER korrektes Markdown-LaTeX. 
   - Für einzelne Variablen oder Terme im Textfluss nutze jeweils ein Dollarzeichen am Anfang und am Ende.
   - Für wichtige, abgesetzte Formeln nutze jeweils zwei Dollarzeichen am Anfang und am Ende.
   - Nutze niemals einfache Klammern wie (x=20) als Mathe-Ersatz. Nutze keine ungewöhnlichen Anführungszeichen.

Gesprächsführung:
Da der Schüler die Aufgaben in der Seitenleiste sieht, musst du sie nicht mehr komplett vorlesen. Frage im ersten Schritt einfach, welche zwei Dinge bei der jeweiligen Aufgabe unbekannt sind.
"""

# 5. Chat-Verlauf und automatische Begrüßung initialisieren
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]
    
    # Automatischer Start: Die erste Nachricht des Bots
    start_msg = "Hallo! 👋 Ich bin dein Mathe-Coach. Links in der Leiste siehst du unsere 3 Aufgaben für heute. Wenn du bereit bist, lass uns mit Aufgabe 1 (Hühner & Schweine) starten. \n\nWelche zwei Dinge suchen wir in dieser Aufgabe eigentlich?"
    st.session_state.messages.append({"role": "assistant", "content": start_msg})

# 6. Bisherige Nachrichten anzeigen (außer System-Prompt)
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 7. Chat-Eingabe für den User
user_input = st.chat_input("Schreibe deine Antwort oder Frage hier...")

if user_input:
    # Benutzereingabe anzeigen & speichern
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # KI Antwort generieren
    with st.chat_message("assistant"):
        try:
            # Hier nutzt du das Modell, das bei dir am besten und schnellsten lief
            stream = client.chat.completions.create(
                model="openai/gpt-oss-20b", 
                messages=st.session_state.messages,
                stream=True
            )
            response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Es gab ein Problem: {e}")
