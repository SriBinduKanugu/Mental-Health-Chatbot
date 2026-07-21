import streamlit as st

# 🔥 REMOVE HEADER
st.markdown("""
<style>
[data-testid="stHeader"] {display: none;}
[data-testid="stToolbar"] {display: none;}
[data-testid="stDecoration"] {display: none;}

.block-container {padding-top: 0rem;}

/* BACKGROUND */
.stApp {background: #F3F0FF;}

/* CARD */
.card {
    width: 380px;
    margin: auto;
    margin-top: 80px;
    padding: 35px;
    background: #FFFFFF;
    border-radius: 20px;
    box-shadow: 0px 10px 30px rgba(124,108,242,0.2);
}

/* TITLE */
.title {
    text-align: center;
    font-size: 32px;
    font-weight: bold;
    color: #7C6CF2;
}

.subtitle {
    text-align: center;
    margin-bottom: 20px;
}

/* INPUT */
.stTextInput input {
    border-radius: 30px !important;
    padding: 14px !important;
    border: 1px solid #ddd !important;
}

/* BUTTON */
.stButton > button {
    width: 100%;
    border-radius: 30px;
    background: linear-gradient(135deg, #7C6CF2, #5A4FCF);
    color: white;
    font-weight: bold;
    padding: 12px;
}

/* CHAT */
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-top: 20px;
}

/* USER BUBBLE */
.user-msg {
    align-self: flex-end;
    background: #6a1b9a;
    color: #ffffff;
    padding: 12px 18px;
    border-radius: 25px 25px 5px 25px;
    max-width: 70%;
}

/* BOT BUBBLE */
.bot-msg {
    align-self: flex-start;
    background: #f3e5f5;
    color: #333333;
    padding: 12px 18px;
    border-radius: 25px 25px 25px 5px;
    max-width: 70%;
    border: 1px solid #eee;
}
</style>
""", unsafe_allow_html=True)


import os
import hashlib
from openai import OpenAI
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

st.set_page_config(page_title="VibeLift", layout="centered")

# ENV
load_dotenv()

# FIREBASE
cred = credentials.Certificate("serviceAccountKey.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

# OPENAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# HASH
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

# SESSION
if "page" not in st.session_state:
    st.session_state.page = "login"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "chat_1"
if "email" not in st.session_state:
    st.session_state.email = None

# DB
def save_user(u,e,p):
    db.collection("users").document(e).set({
        "username":u,"email":e,"password":p
    })

def check_login(e,p):
    user = db.collection("users").document(e).get()
    return user.exists and user.to_dict()["password"] == hash_password(p)

def load_chats(e):
    chats = db.collection("users").document(e).collection("chats").stream()
    return {c.id:c.to_dict().get("messages",[]) for c in chats} or {"chat_1":[]}

def save_chat(e,id,data):
    db.collection("users").document(e).collection("chats").document(id).set({
        "messages":data
    })

# LOGIN
def login():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="title">VibeLift</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Login</div>', unsafe_allow_html=True)

    e = st.text_input("Email")
    p = st.text_input("Password", type="password")

    if st.button("Sign In"):
        if check_login(e,p):
            st.session_state.page = "chatbot"
            st.session_state.email = e
            st.rerun()
        else:
            st.error("Invalid credentials")

    if st.button("Create Account"):
        st.session_state.page = "signup"
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# SIGNUP
def signup():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="title">VibeLift</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Register</div>', unsafe_allow_html=True)

    u = st.text_input("Username")
    e = st.text_input("Email")
    p = st.text_input("Password", type="password")
    cp = st.text_input("Confirm Password", type="password")

    if st.button("Register"):
        if p != cp:
            st.error("Passwords mismatch")
        elif not (u and e and p):
            st.error("Fill all fields")
        else:
            save_user(u,e,hash_password(p))
            st.success("Account created")
            st.session_state.page = "login"
            st.rerun()

    if st.button("Back"):
        st.session_state.page = "login"
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# CHATBOT
def chatbot():
    st.title("💜 VibeLift Chatbot")

    e = st.session_state.email
    chats = load_chats(e)

    if st.session_state.current_chat not in chats:
        save_chat(e, st.session_state.current_chat, [])

    with st.sidebar:
        st.header("Chats")

        for c in chats:
            if st.button(c):
                st.session_state.current_chat = c
                st.session_state.chat_history = chats[c]
                st.rerun()

        if st.button("New Chat"):
            name = f"chat_{len(chats)+1}"
            save_chat(e, name, [])
            st.session_state.current_chat = name
            st.session_state.chat_history = []
            st.rerun()

        if st.button("Logout"):
            st.session_state.page = "login"
            st.session_state.email = None
            st.rerun()

    # 🔥 SMART RESPONSE FUNCTION
    def get_response(user_input):
        try:
            messages = []

            messages.append({
                "role": "system",
                "content": (
                    "You are a supportive mental health chatbot.\n"
                    "- Focus on emotions, stress, mental health, studies, wellbeing\n"
                    "- Allow greetings like hi, hello\n"
                    "- If user clearly asks unrelated topics, say:\n"
                    "'I’m here to support mental health concerns 💜. Tell me how you're feeling.'\n"
                    "- Be empathetic and friendly\n"
                    "- Give clear and useful advice\n"
                    "- Keep answers short\n"
                    "- Remember conversation context\n"
                    "- If user seems in distress, suggest professional help"
                )
            })

            for chat in st.session_state.chat_history[-6:]:
                role = "user" if chat["sender"] == "You" else "assistant"
                messages.append({"role": role, "content": chat["message"]})

            messages.append({"role": "user", "content": user_input})

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_completion_tokens=160,
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error: {str(e)}"

    msg = st.chat_input("Type your message...")

    if msg:
        st.session_state.chat_history.append({"sender":"You","message":msg})
        reply = get_response(msg)
        st.session_state.chat_history.append({"sender":"Bot","message":reply})
        save_chat(e, st.session_state.current_chat, st.session_state.chat_history)

    # CHAT UI
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for c in st.session_state.chat_history:
        if c["sender"] == "You":
            st.markdown(f'<div class="user-msg">{c["message"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-msg">{c["message"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ROUTING
if st.session_state.page == "login":
    login()
elif st.session_state.page == "signup":
    signup()
else:
    chatbot()                 bro ppt lo code pettali so ae ae snippets pettalo cheppu important vi main vi
