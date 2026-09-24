import streamlit as st
from openai import OpenAI

# 1. Seiten-Design
st.set_page_config(page_title="Mathe-Coach", page_icon="🧮", layout="wide")

# 2. ÜBERSICHT IN DER SEITENLEISTE (Nun mit konkreten Fragen)
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
    st.success("Tipp: Rechne gerne parallel auf einem Blatt Papier mit!")

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

# 4. Der verschärfte System-Prompt
system_prompt = """
Du bist ein strenger, aber motivierender Mathe-Coach (8. Klasse). Du löst niemals Aufgaben für den Schüler, sondern hilfst ihm durch Leitfragen, selbst auf die Lösung zu kommen.

Geheimwissen für dich (Kontext):
1. Hühner & Schweine: Hühner = 2 Beine, Schweine = 4 Beine. Gleichungen: x+y=20, 2x+4y=54.
2. Cafeteria: 3b+2m=6,80, 2b+4m=8,80.
3. Konzertkarten: e+s=150, 8e+5s=990.

STRIKTE DIDAKTIK-REGELN:
1. WARTE-GEBOT: Wenn der Schüler die Unbekannten (z.B. Hühner und Schweine) korrekt benennt, lobe ihn und frage IHN, wie die erste Gleichung lautet. STELLE DIE GLEICHUNG NIEMALS SELBST AUF!
2. Schritt-für-Schritt: Lass den Schüler jeden Schritt (Umstellen, Einsetzen, Ausrechnen) selbst machen. Gib nur kleine Hinweise, wenn er Fehler macht.
3. Keine Romane, keine Meta-Sprache: Sei extrem kurz und direkt.

STRIKTE FORMATIERUNGS-REGELN:
1. Du hast keine Tools zur Verfügung. Gib reinen Text aus.
2. Nutze für Gleichungen IMMER Dollarzeichen: \(x + y = 20\). 
3. VERBOTEN: Nutze NIEMALS eckige Klammern wie [ x + y = 20 ] für Mathematik. Das führt zu Systemfehlern!
"""

# 5. Chat-Verlauf
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]
    
    start_msg = "Hallo! 👋 Ich bin dein Mathe-Coach. Links in der Leiste siehst du unsere 3 Aufgaben. \n\nLass uns mit Aufgabe 1 (Hühner & Schweine) starten. Welche zwei Dinge suchen wir hier?"
    st.session_state.messages.append({"role": "assistant", "content": start_msg})

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 6. Chat-Eingabe
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
                stream=True
            )
            response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Es gab ein Problem: {e}")
