import streamlit as st
import google.generativeai as genai

# 1. Seiten-Design festlegen
st.set_page_config(page_title="Mathe-Coach", page_icon="🧮")
st.title("🧮 Dein interaktiver Mathe-Coach")
st.write("Heute bearbeiten wir Aufgaben zu Linearen Gleichungssystemen. Ich bin hier, um dich zu unterstützen!")

# 2. API-Key sicher laden (wird später in Streamlit hinterlegt)
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Bitte hinterlege den API-Key in den Streamlit Secrets.")

# 3. Den System-Prompt definieren (Das didaktische Gehirn)
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
4. Formatives Feedback: Zähle intern mit, wie viel Hilfe nötig war. Am Ende aller Aufgaben gibst du ein Feedback zur *Selbstständigkeit* (z.B. "Aufgabe 1 hast du fast komplett alleine gelöst..."). Keine Noten vergeben!
Sei ermutigend und lobe Teilerfolge.
"""

# 4. KI-Modell initialisieren
model = genai.GenerativeModel(
    model_name="models/gemini-3.1-pro-preview",
    system_instruction=system_prompt
)

# 5. Chat-Verlauf speichern
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

# 6. Bisherige Nachrichten auf dem Bildschirm anzeigen
for message in st.session_state.chat.history:
    role = "assistant" if message.role == "model" else "user"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# 7. Eingabefeld für die Schüler
user_input = st.chat_input("Deine Antwort oder Frage...")

if user_input:
    # Benutzereingabe anzeigen
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # KI-Antwort generieren und anzeigen
    with st.chat_message("assistant"):
        response = st.session_state.chat.send_message(user_input)
        st.markdown(response.text)
