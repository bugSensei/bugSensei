import os
import streamlit as st
from mistralai import Mistral

st.set_page_config(page_title="BugSensei", layout="wide")
client = Mistral(api_key=st.secrets['MISTRAL_API_KEY'])
def run_mistral(user_message, model="mistral-large-latest"):
    messages = [{"role": "user", "content": user_message}]
    chat_response = client.chat.complete(model=model, messages=messages)
    return chat_response.choices[0].message.content


st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans:ital,wght@0,100..900;1,100..900&family=Roboto+Flex:opsz,wght@8..144,100..1000&family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap');

.chat-container {
    display: flex;
    flex-direction: column;
    width: 100%;
    background-color:#403d39;
}

.user-message, .assistant-message {
    border-radius: 20px;
    background-color:#eb5e28;
    padding: 15px;
    margin-bottom: 15px;
    max-width: 70%;
    width: fit-content;
    word-wrap: break-word;
    overflow-wrap: break-word;
    color:#fffcf2;
    font-size:18px;
    font-family: "Noto Sans", serif;
    font-weight: 400;
    font-style: normal;
    
}

.user-message {
    align-self: flex-end;
    margin-left: auto;
    text-align: left;
    
}

.assistant-message {
    align-self: flex-start;
    margin-right: auto;
    text-align: left;
    background-color:#e63946
}
</style>
""",
    unsafe_allow_html=True,
)

st.title("BugSensei")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Let's fix your computer, shall we?"}
    ]


st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for message in st.session_state.messages:
    if message["role"] == "user":

        st.markdown(
            f'<div class="user-message">{message["content"]}</div>',
            unsafe_allow_html=True,
        )
    else:

        st.markdown(
            f'<div class="assistant-message">{message["content"]}</div>',
            unsafe_allow_html=True,
        )


st.markdown("</div>", unsafe_allow_html=True)


if prompt := st.chat_input("Type your message here..."):

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f'<div class="user-message">{prompt}</div>', unsafe_allow_html=True)

    with st.spinner("Let me see..."):
        full_response = run_mistral(prompt)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.markdown(
        f'<div class="assistant-message">{full_response}</div>', unsafe_allow_html=True
    )
