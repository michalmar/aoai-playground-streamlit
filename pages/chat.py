import streamlit as st
import os
import json
# Note: DALL-E 3 requires version 1.0.0 of the openai-python library or later
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from prompts import PROMPTS_SYSTEM_LIST

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# MODEL = os.environ['AZURE_OPENAI_MODEL_NAME']
# MODEL = "gpt-35-turbo"

SYSTEM_DEFAULT_PROMPT = "Assistant is a large language model trained by OpenAI."


if "info" not in st.session_state:
    st.session_state.info = None
if "SYSTEM_PROMPT" not in st.session_state:
    st.session_state.SYSTEM_PROMPT = SYSTEM_DEFAULT_PROMPT
if "messages" not in st.session_state:
    st.session_state.messages = [
                    {"role": "system", "content": st.session_state.SYSTEM_PROMPT},
                ]
if "model" not in st.session_state:
    st.session_state.model = "gpt-35-turbo"
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.5
if "max_tokens" not in st.session_state:
    st.session_state.max_tokens = 200


AZURE_OPENAI_MODELS_DEPLOYEMNTS = os.environ['AZURE_OPENAI_MODELS_DEPLOYEMNTS']

token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")

#################################################################################
# App elements

st.set_page_config(layout="wide")
st.title("Chat Playground")

with st.sidebar:
    st.caption("Settings")
    st.session_state.model = st.selectbox("Select a model", AZURE_OPENAI_MODELS_DEPLOYEMNTS.split(","))
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

    

st.caption(f"powered by Azure OpenAI's {st.session_state.model} model")
# st.caption(f"powered by Azure OpenAI's {MODEL} model")

for message in st.session_state.messages:
    if message["role"] == "system":
        pass
    else:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


# Accept user input
if prompt := st.chat_input("What is up?"):
    if prompt:
        
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

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
            
            response = client.chat.completions.create(
                model = st.session_state.model ,
                messages=st.session_state.messages,
                stream=True,
                temperature=st.session_state.temperature,
                max_tokens=st.session_state.max_tokens,
            )
            
            for part in response:
                # st.write(part)
                if len(part.choices) > 0:
                    full_response += part.choices[0].delta.content or ""
                    message_placeholder.markdown(full_response + "▌")

            # final response
            message_placeholder.markdown(full_response)

            # add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
             
    
