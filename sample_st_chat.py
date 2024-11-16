# streamlit basic code:
import streamlit as st
import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------------------
# Required Classes:
# ---------------------------------------------------------------------------------------


class media:
    def __init__(self, type=None, path=None):
        self.type = type
        self.path = path

        if not type:
            self.isAvailable = False
        else:
            self.isAvailable = True

    def get_media(self):
        if self.type == 'image':
            a, b = st.columns([0.8, 9.2])
            with a:
                st.write("")
            with b:
                st.image(self.path, width=450)
        elif self.type == 'audio':
            return st.audio(self.path)
        elif self.type == 'video':
            return st.video(self.path)
        else:
            return None


if 'messages' not in st.session_state:
    st.session_state.messages = [
        {
            "role": "Bot",
            "content": "Hello 👋, How may I help you?",
            "media": media()
        },
        {
            "role": "User",
            "content": "This is my query",
            "media": media("image", "./assets/visualization.png")},
        {
            "role": "Bot",
            "content": "Just google it 😁",
            "media": media()},
        {
            "role": "User",
            "content": "Timepass media content:",
            "media": media("image", "https://plus.unsplash.com/premium_photo-1664474619075-644dd191935f")
        }
    ]

st.subheader(':blue[GenAI Assistant Local] ✨', divider='rainbow')

inp = st.chat_input('Your message')
# st.write(st.session_state.messages)

if inp:
    st.session_state.messages.append(
        {"role": "User", "content": inp, "media": media()})
    st.session_state.messages.append(
        {"role": "Bot", "content": f"Same: {inp} 😹", "media": media()})

# with st.chat_message("user"):
#     st.write("Hello 👋")

for message in st.session_state.messages:
    if message['role'].lower() == 'user':
        with st.chat_message("user", avatar='🕵️'):
            st.write(message['content'])

    else:
        with st.chat_message("ai"):
            st.write(message['content'])

    if message['media'].isAvailable:
        message['media'].get_media()
