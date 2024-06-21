import streamlit as st
import os
import json
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# MODEL = os.environ['AZURE_OPENAI_MODEL_NAME']
# MODEL = "gpt-35-turbo"

SYSTEM_DEFAULT_PROMPT = "You are a helpful assistant."
AZURE_OPENAI_VISION_MODEL_DEPLOYEMNTS = os.environ['AZURE_OPENAI_VISION_MODEL_DEPLOYEMNTS']


if "info" not in st.session_state:
    st.session_state.info = None
if "SYSTEM_PROMPT" not in st.session_state:
    st.session_state.SYSTEM_PROMPT = SYSTEM_DEFAULT_PROMPT
if "messages" not in st.session_state:
    st.session_state.messages = [
                    {"role": "system", "content": st.session_state.SYSTEM_PROMPT},
                ]
if "model" not in st.session_state:
    st.session_state.model = "gpt-4-turbo"
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.5
if "max_tokens" not in st.session_state:
    st.session_state.max_tokens = 200

token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")

#################################################################################
# App elements

st.set_page_config(layout="wide")
st.title("Completion with Vision model")

def prepare_to_save():
    session_setup = {}
    session_setup["model"] = st.session_state.model
    session_setup["temperature"] = st.session_state.temperature
    session_setup["max_tokens"] = st.session_state.max_tokens
    session_setup["SYSTEM_PROMPT"] = st.session_state.SYSTEM_PROMPT
    session_setup["messages"] = st.session_state.messages
    return session_setup

with st.sidebar:
    st.caption("Settings")
    # vehicle_feature_display = st.json(st.session_state.vehicle_features)
    st.session_state.model = st.selectbox("Select a model", AZURE_OPENAI_VISION_MODEL_DEPLOYEMNTS.split(","))
    st.session_state.temperature = st.slider("Temperature", 0.0, 1.0, 0.5, 0.01)
    st.session_state.max_tokens = st.slider("Max tokens", 100, 4000, 800, 100)
        
    st.text_area("Enter your SYSTEM message", key="system_custom_prompt", value=st.session_state.SYSTEM_PROMPT)
    if st.button("Apply & Clear Memory"):
        # save the text from the text_area to SYSTEM_PROMPT
        st.session_state.SYSTEM_PROMPT = st.session_state.system_custom_prompt
        st.session_state.messages = [
                        {"role": "system", "content": st.session_state.SYSTEM_PROMPT},
                    ]
    st.caption("Refresh the page to reset to default settings")

    if st.button("Download setup as JSON"):
        session_data = prepare_to_save()
        st.write("perpared")
        st.download_button(
                    label="💾 Download",
                    data=json.dumps(session_data, indent=4, ensure_ascii=False).encode('utf-8'),
                    file_name='setup.json',
                    mime='application/json'
                )

    

# st.caption(f"powered by Azure OpenAI's {st.session_state.model} model")
# st.caption(f"powered by Azure OpenAI's {MODEL} model")

for message in st.session_state.messages:
    if message["role"] == "system":
        pass
    elif message["role"] == "tool":
        pass
    else:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


# create text input for user to enter a prompt
prompt = st.text_area("Enter your prompt", value="Describe this picture:", height=100)

if prompt.strip() == "":
    prompt = "Describe this picture:"

import base64
uploaded_file = st.file_uploader("Upload a file to ground your answers", type=["png", "jpg", "jpeg"])
if uploaded_file is not None:
    uploaded_file.seek(0)
    ulpoaded_file_bytes = uploaded_file.read()
    base64_encoded_image = base64.b64encode(ulpoaded_file_bytes).decode('ascii')

    # display the image
    st.image(uploaded_file, caption="Uploaded Image", width=200)

if st.button("Submit"):
    # st.session_state.messages.append({"role": "user", "content": prompt})

    if os.environ["AZURE_OPENAI_API_KEY"] == "":
        # using managed identity
        client = AzureOpenAI(
            api_version=os.environ['AZURE_OPENAI_API_VERSION'],
            base_url=f"{os.environ['AZURE_OPENAI_ENDPOINT']}/openai/deployments/{st.session_state.model}",
            azure_ad_token_provider=token_provider,
        )
    else:
        # using api key
        client = AzureOpenAI(
            api_version=os.environ['AZURE_OPENAI_API_VERSION'],
            base_url=f"{os.environ['AZURE_OPENAI_ENDPOINT']}/openai/deployments/{st.session_state.model}",
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
        )

    st.session_state.messages.append({"role": "user", "content": prompt}) 

    response = client.chat.completions.create(
        model=st.session_state.model,
        messages=[
            { "role": "system", "content": f"{st.session_state.SYSTEM_PROMPT}" },
            { "role": "user", "content": [  
                { 
                    "type": "text", 
                    "text": f"{prompt}" 
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_encoded_image}"
                    }
                }
            ] } 
        ],
        max_tokens=st.session_state.max_tokens,
        temperature=st.session_state.temperature
    )

    st.write("## Completion result:")
    st.write(response.choices[0].message.content)
    # add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response.choices[0].message.content})



