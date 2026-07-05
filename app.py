import streamlit as st
import json
import random
with open('intents.json', encoding='utf-8') as f:
    intents = json.load(f)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "last_tag" not in st.session_state:
    st.session_state.last_tag = None

if "user_input" not in st.session_state:
    st.session_state.user_input = ""
def get_response(user_input):
    text = user_input.lower()
    last_tag = st.session_state.last_tag

    if any(w in text for w in ["suicide","sucide","sucid","kill myself","end my life","die","want to die"]):
        tag = "suicide"

    elif any(w in text for w in ["sad","depress","down","low","not ok","not okay","not fine"]):
        tag = "sad"

    elif any(w in text for w in ["stress","pressure","tension","overwhelmed"]):
        tag = "stress"

    elif any(w in text for w in ["study","studies","exam","marks","focus"]) or (last_tag == "stress" and any(w in text for w in ["my studies","study","studies"])):
        tag = "study_help"

   
    elif any(w in text for w in ["tired","exhaust","drained"]):
        tag = "tired"

  
    elif "bored" in text:
        tag = "bored"

   
    elif any(w in text for w in ["fine","okay","ok","good","happy"]):
        tag = "positive"

   
    elif any(w in text for w in ["fuck","shit","fucking"]):
        tag = "abuse"

   
    elif any(w in text for w in ["hi","hello","hey"]):
        tag = "greeting"

   
    else:
        tag = "default"

   
    st.session_state.last_tag = tag

   
    for intent in intents["intents"]:
        if intent["tag"] == tag:
            return random.choice(intent["responses"])

    return "I'm here to listen ❤️"

st.set_page_config(page_title="Mental Health Chatbot", page_icon="💬")
st.title("💬 Mental Health Chatbot")
st.write("I'm here to listen and support you ❤️")
def submit_input():
    user_input = st.session_state.user_input
    if user_input.strip() != "":
        response = get_response(user_input)
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("Bot", response))
        st.session_state.user_input = ""  # clear input after sending


chat_box = st.container()
with chat_box:
    for sender, message in st.session_state.chat_history:
        if sender == "You":
            st.markdown(f"🧑 You: {message}")
        else:
            st.markdown(f"🤖 Bot: {message}")

st.text_input("Type your message...", key="user_input", on_change=submit_input, placeholder="Type here and press Enter...")