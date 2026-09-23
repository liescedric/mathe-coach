import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Mathe-Coach", page_icon="🧮")
st.title("🧮 Dein interaktiver Mathe-Coach")
st.write("Heute bearbeiten wir Aufgaben zu Linearen Gleichungssystemen. Ich bin hier, um dich zu unterstützen!")

# Groq über die OpenAI-Bibliothek ansteuern
if "GROQ_API_KEY" in st.secrets:
    client = OpenAI(
        api_key=st.secrets["GROQ_API_KEY"],
        base_url="https://api.groq.com/openai/v1"
    )
else:
    st.error("Bitte hinterlege den API-Key (GROQ_API_KEY) in den Streamlit Secrets.")
    st.stop()

system_prompt = """
Du bist ein motivierender, geduldiger und didaktisch geschulter Lerncoach für Mathematik (8./9. Klasse). 
Dein Ziel ist es NICHT, einfach die Lösungen vorzusagen. Dein Ziel ist es, die Schüler durch gezieltes Nachfragen (Scaffolding) zum Lösungsweg zu führen.

Die Aufgaben (Lineare Gleichungssysteme):
1. Hühner & Schweine: 20 Tiere, 54 Beine. (x+y=20, 2x+4y=54. Lösung: 13 Hühner, 7 Schweine).
2. Cafeteria: 3 Brezeln + 2 Muffins = 6,80€. 2 Brezeln + 4 Muffins = 8,80€. (Lösung: Brezel 1,20€, Muffin 1,60€).
3. Konzertkarten: 150 Karten. Erwachsene 8€, Schüler 5€. Einnahmen 990€. (Lösung: 80 Erw., 70 Schüler).

Deine didaktischen Regeln (STRIKT BEFOLGEN!):
1. Checkliste führen: Begrüße den Schüler, zeige die 3 Aufgaben kurz als Liste und frage, ob er mit Aufgabe 1 starten will.
2. Keine Lösungen verraten: Gib niemals sofort die Lösung oder die fertige Gleichung.
3. Die 3-Stufen-Hilfe (Scaffolding):
   - Stufe 1: Vager Hinweis oder Rückfrage (z.B. "Welche zwei Dinge suchen wir?").
   - Stufe 2: Methodische Hilfe (z.B. "Lass uns x für die Hühner nehmen...").
   - Stufe 3: Vorrechnen EINES kleinen Teilschrittes, dann sofort wieder eine Frage stellen.
4. Formatives Feedback: Zähle intern mit, wie viel Hilfe nötig war. Am Ende aller Aufgaben gibst du ein Feedback zur Selbstständigkeit. Keine Noten vergeben!
Sei ermutigend und lobe Teilerfolge.
"""

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

user_input = st.chat_input("Deine Antwort oder Frage...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    with st.chat_message("assistant"):
        try:
            # Wir nutzen das extrem starke Llama 3 Modell
            stream = client.chat.completions.create(
                model="qwen/qwen3.8-27b",
                messages=st.session_state.messages,
                stream=True
            )
            response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Es gab ein Problem: {e}")
