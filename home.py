import streamlit as st
import os

if "info" not in st.session_state:
    st.session_state.info = None
#################################################################################
# App elements

st.set_page_config(layout="wide")
st.title("Azure OpenAI Playground")

text = '''
This is a simplified playground of Azure OpenAI API in simple web app.

Supported scenarios & APIs:
- :speech_balloon: [Chat](./chat) simple ChatGPT-like app
- :frame_with_picture: [Completion](./completion) simple completion
- :eye: [GPT-4 Vision](./vision) Showcase of GPT-4 Vision API
'''

st.markdown(text)