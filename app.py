import streamlit as st
from openai import OpenAI

# 1. Seiten-Design
st.set_page_config(page_title="Mathe-Coach", page_icon="🧮", layout="wide")

# 2. ÜBERSICHT IN DER SEITENLEISTE
with st.sidebar:
    st.title("📝 Deine Aufgaben")
    st.markdown("""
    **Aufgabe 1: Hühner & Schweine**
    Auf einem Bauernhof gibt es Hühner und Schweine. Insgesamt sind es 20 Tiere. Zusammen haben sie 54 Beine. 
    *Frage: Wie viele Hühner und wie viele Schweine sind es?*
    
    **Aufgabe 2: Cafeteria**
    Anna kauft 3 Brezeln und 2 Muffins für 6,80€. Ben kauft 2 Brezeln und 4 Muffins für 8,80€. 
    *Frage: Wie viel kostet eine Brezel und wie viel ein Muffin?*
    
    **Aufgabe 3: Konzertkarten**
    Für ein Schulkonzert wurden 150 Karten verkauft. Erwachsene 8€, Schüler 5€. Einnahmen 990€.
    *Frage: Wie viele Erwachsene und wie viele Schüler waren auf dem Konzert?*
    """)
    st.divider()
    st.title("📄 Dein Notizzettel")
    st.info("Hier halten wir unsere aktuellen Gleichungen fest:")
    # Platzhalter für den Notizzettel
    notizzettel_platzhalter = st.empty()

st.title("🧮 Dein interaktiver Mathe-Coach")

# 3. API-Key laden
if "GROQ_API_KEY" in st.secrets:
    client = OpenAI(
        api_key=st.secrets["GROQ_API_KEY"],
        base_url="https://api.groq.com/openai/v1"
    )
else:
    st.error("Bitte hinterlege den API-Key (GROQ_API_KEY) in den Streamlit Secrets.")
    st.stop()

# 4. Der System-Prompt (mit Fokus auf Passivität und Flexibilität)
system_prompt = """
Du bist ein Mathe-Coach (8. Klasse). Du begleitest den Schüler bei der Lösung, aber DU GIBST NIEMALS DEN NÄCHSTEN RECHENSCHRITT VOR.

Geheimwissen für dich (Kontext):
1. Hühner & Schweine: Hühner = 2 Beine, Schweine = 4 Beine. (x+y=20, 2x+4y=54)
2. Cafeteria: 3 Brezeln + 2 Muffins = 6,80 Euro; 2 Brezeln + 4 Muffins = 8,80 Euro
3. Konzertkarten: e+s=150, 8e+5s=990

STRIKTE DIDAKTIK-REGELN:
1. FREIE WAHL: Lass den Schüler entscheiden, welche Aufgabe er bearbeiten will.
2. FLEXIBLE VARIABLEN: Akzeptiere JEDE Variablen-Zuweisung des Schülers (z.B. wenn er m=Brezel wählt, dann ist das so!). Korrigiere ihn nicht, passe dich an.
3. ABSOLUTES WARTE-GEBOT: Wenn der Schüler eine Gleichung aufstellt oder umstellt, bestätige NUR, dass es richtig ist, und frage: "Was möchtest du als Nächstes tun?" oder "Wie geht es jetzt weiter?". RECHNE NIEMALS SELBST! Fasse keine Terme zusammen.
4. "Ich weiß nicht": Wenn der Schüler nicht weiterweiß, gib EINEN kleinen Tipp (z.B. "Erinnerst du dich an das Einsetzungsverfahren?"). Löse die Aufgabe nicht auf.

STRIKTE FORMATIERUNGS-REGELN:
1. Nutze für Variablen und Formeln IMMER das korrekte Markdown-Math-Format. Schreibe ein Dollarzeichen vor und nach der Formel.
2. VERBOTEN: Nutze NIEMALS normale Klammern um mathematische Ausdrücke, z.B. (x=20) oder ((x+y=20)). Das macht es unleserlich.
3. Am Ende DEINER JEDEN Antwort schreibst du zwingend das Wort "NOTIZZETTEL:" gefolgt von den aktuell gültigen Gleichungen oder Variablen, die ihr bisher herausgefunden habt. (Beispiel: NOTIZZETTEL: m: Brezel, b: Muffin, 3m + 2b = 6.80).
"""

# 5. Chat-Verlauf und Notizzettel initialisieren
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]
    start_msg = "Hallo! 👋 Ich bin dein Mathe-Coach. Links in der Leiste siehst du unsere 3 Aufgaben. \n\nMit welcher Aufgabe möchtest du beginnen?"
    st.session_state.messages.append({"role": "assistant", "content": start_msg})

if "notizzettel" not in st.session_state:
    st.session_state.notizzettel = "Noch leer. Wir fangen gerade erst an!"

# Notizzettel in der Sidebar aktualisieren
notizzettel_platzhalter.markdown(st.session_state.notizzettel)

# 6. Bisherige Nachrichten anzeigen
for msg in st.session_state.messages:
    if msg["role"] != "system":
        # Wir blenden den Notizzettel-Teil im Chat aus, da er in die Sidebar gehört
        display_text = msg["content"].split("NOTIZZETTEL:")[0].strip()
        with st.chat_message(msg["role"]):
            st.markdown(display_text)

# 7. Chat-Eingabe
user_input = st.chat_input("Schreibe deine Antwort oder Frage hier...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    with st.chat_message("assistant"):
        try:
            stream = client.chat.completions.create(
                model="openai/gpt-oss-20b", 
                messages=st.session_state.messages,
                stream=False # Stream=False erleichtert das Parsen des Notizzettels
            )
            full_response = stream.choices[0].message.content
            
            # Notizzettel extrahieren und im Session State speichern
            if "NOTIZZETTEL:" in full_response:
                chat_text, notizzettel_text = full_response.split("NOTIZZETTEL:")
                st.session_state.notizzettel = notizzettel_text.strip()
            else:
                chat_text = full_response
            
            st.markdown(chat_text.strip())
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # Sidebar direkt aktualisieren (erfordert Rerun in Streamlit)
            st.rerun()
            
        except Exception as e:
            st.error(f"Es gab ein Problem: {e}")
