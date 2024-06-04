import streamlit as st
import os
import json
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from prompts import PROMPTS_SYSTEM_LIST

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())




if "info" not in st.session_state:
    st.session_state.info = None
if "SYSTEM_PROMPT" not in st.session_state:
    st.session_state.SYSTEM_PROMPT = PROMPTS_SYSTEM_LIST["Default prompt"]

if "model" not in st.session_state:
    st.session_state.model = "gpt-35-turbo"
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.5
if "max_tokens" not in st.session_state:
    st.session_state.max_tokens = 200

MODEL = st.session_state.model
token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")
AZURE_OPENAI_MODELS_COMPLETION_DEPLOYEMNTS = os.environ['AZURE_OPENAI_MODELS_COMPLETION_DEPLOYEMNTS']
#################################################################################
# App elements

st.set_page_config(layout="wide")
st.title("Completion Playground")

with st.sidebar:
    st.caption("Settings")
    st.session_state.model = st.selectbox("Select a model", AZURE_OPENAI_MODELS_COMPLETION_DEPLOYEMNTS.split(","))
    st.session_state.temperature = st.slider("Temperature", 0.0, 1.0, 0.5, 0.01)
    st.session_state.max_tokens = st.slider("Max tokens", 100, 4000, 800, 100)

    # Create a selectbox with the dictionary items
    selected_option = st.selectbox(
        'Select an option:',
        list(PROMPTS_SYSTEM_LIST.keys())
    )

    # Get the value of the selected option
    selected_value = PROMPTS_SYSTEM_LIST[selected_option]

    st.session_state.SYSTEM_PROMPT = selected_value

    # st.write(f"You selected {selected_option}, which corresponds to {selected_value}")

    st.text_area("Enter your SYSTEM message", key="system_custom_prompt", value=st.session_state.SYSTEM_PROMPT)

    if st.button("Apply & Clear Memory"):
        # save the text from the text_area to SYSTEM_PROMPT
        st.session_state.SYSTEM_PROMPT = st.session_state.system_custom_prompt
        st.session_state.messages = [
                        {"role": "system", "content": st.session_state.SYSTEM_PROMPT},
                    ]
    st.caption("Refresh the page to reset to default settings")


st.caption(f"powered by Azure OpenAI's {MODEL} model")

st.text_area("Create your prompt here", key="pitch", value="Write a list of colors. Output as list of JSONs.")

c1,c2, c3 = st.columns([2,8,1])

with c1:

    # button to submit the form
    if st.button("Generate"):
        # st.session_state.pitch = st.session_state.pitch

        if st.session_state.pitch:

            if os.environ["AZURE_OPENAI_API_KEY"] == "":
                # using managed identity
                client = AzureOpenAI(
                    api_version=os.environ['AZURE_OPENAI_API_VERSION'],
                    azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT'],
                    azure_ad_token_provider=token_provider,
                )
            else:
                # using api key
                client = AzureOpenAI(
                    api_version=os.environ['AZURE_OPENAI_API_VERSION'],
                    azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT'],
                    api_key=os.environ["AZURE_OPENAI_API_KEY"],
                ) 


            # get text from text area
            pitch = st.session_state.pitch

            msgs = [
                        {"role": "system", "content": st.session_state.SYSTEM_PROMPT},
                        {"role": "user", "content": pitch}
                        ]
            
            response = client.chat.completions.create(
                    model = MODEL,
                    messages=msgs
            )

            st.markdown("## Completion result:")
            st.write(response.choices[0].message.content)
       
with c3:
    # clear button
    if st.button("Clear", type="primary"):
        # save the text from the text_area to SYSTEM_PROMPT
        st.session_state.SYSTEM_PROMPT = st.session_state.system_custom_prompt
        st.session_state.messages = [
                        {"role": "system", "content": st.session_state.SYSTEM_PROMPT},
                    ]