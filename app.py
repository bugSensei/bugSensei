import os
import streamlit as st
from mistralai import Mistral
import sys
import json
import tempfile

from utils.eurus import Eurus
from utils.bots.reddit import RedditRetriever
from utils.bots.stackexchange import StackExchangeRetriever
from utils.bots.microsoft_forum import MicrosoftForum
from utils.bots.amd_community import AmdCommunity
from utils.bots.tomsforum import TomsForumRunner
from utils.bots.lenovoforums import LenovoForum


sys.path.append(".")  # necessary for importing files

# st.set_page_config(page_title="BugSensei", layout="wide")
# client = Mistral(api_key=st.secrets['MISTRAL_API_KEY'])

# def run_mistral(user_message, model="mistral-large-latest"):
#     messages = [{"role": "user", "content": user_message}]
#     chat_response = client.chat.complete(model=model, messages=messages)
#     return chat_response.choices[0].message.content


# st.markdown(
#     """
# <style>
# @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;1,100;1,200;1,300;1,400;1,500;1,600;1,700&family=Noto+Sans:ital,wght@0,100..900;1,100..900&family=Roboto+Flex:opsz,wght@8..144,100..1000&family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap');

# [data-testid="stAppViewContainer"]{
# background-color:#f8f9fa;
# }
# [data-testid="stHeader"]{
# background-color:#f8f9fa;
# }
# [data-testid="stTool"]{
# background-color:#f8f9fa;
# }
# [data-testid="stBottomBlockContainer"]{
# background-color:#f8f9fa;
# }

# .stChatInput{
# margin-right:100px;
# background-color:white;

# }
# .st-be{
# color:black;
# }

# .st-bw{
# caret-color:black;
# }

# .heading {
#     display: flex;
#     justify-content: center;
#     align-items: center;
#     font-size: 50px; /* Increase font size */
#     font-family: "IBM Plex Mono", sans-serif; /* Apply imported font */
#     font-weight: 300; /* Adjust font weight if needed */
#     color: black; /* Optional: Change text color */
#     margin: 20px 0; /* Optional: Add spacing */
# }

# .chat-container {
#     display: flex;
#     flex-direction: column;
#     align-items:center;
#     width: 100%;
#     background-color: #403d39;
# }

# .user-message, .assistant-message {
#     border-radius: 10px;
#     /*border: 2px solid white; Add a white outline */
#     background-color: transparent; /* Transparent background */
#     padding-left: 30px;
#     padding-right:30px;
#     padding-top:10px;
#     padding-bottom:10px;
#     margin-bottom: 15px;
#     max-width: 70%;
#     width: fit-content;
#     word-wrap: break-word;
#     overflow-wrap: break-word;
#     color: #232323; /* White text color for visibility */
#     font-size: 18px;
#     font-family: "IBM Plex Mono", serif;
#     font-weight: 400;
#     font-style: normal;
# }

# .user-message {
#     align-self: flex-end;
#     margin-left: auto;
#     text-align: left;
#     background-color:#dee2e6
# }

# .assistant-message {
#     align-self: center;
#     margin-right: 0 auto;
#     text-align: left;
#     background-color:#dee2e6
# }

# </style>
# """,
#     unsafe_allow_html=True,
# )

# st.markdown('<div class="heading">BugSensei</div>', unsafe_allow_html=True)

# if "messages" not in st.session_state:
#     st.session_state.messages = [
#         {"role": "assistant", "content": "Let's fix your computer, shall we?"}
#     ]

# st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# for message in st.session_state.messages:
#     if message["role"] == "user":
#         st.markdown(
#             f'<div class="user-message">{message["content"]}</div>',
#             unsafe_allow_html=True,
#         )
#     else:
#         st.markdown(
#             f'<div class="assistant-message">{message["content"]}</div>',
#             unsafe_allow_html=True,
#         )

# st.markdown("</div>", unsafe_allow_html=True)

# if prompt := st.chat_input("Type your message here..."):
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     st.markdown(f'<div class="user-message">{prompt}</div>', unsafe_allow_html=True)

#     with st.spinner():
#         full_response = run_mistral(prompt)
#     st.session_state.messages.append({"role": "assistant", "content": full_response})
#     st.markdown(
#         f'<div class="assistant-message">{full_response}</div>', unsafe_allow_html=True
#     )

# working commit - finally ##
def main():
    st.title("Testing Eurus")
    # st.text(st.secrets['REDDIT_USERNAME'])
    # st.text(st.secrets["REDDIT_SECRET_KEY"])
    # st.text(st.secrets["REDDIT_PASSWORD"],)
    # st.text()
    current_cwd = os.getcwd()

    # Define the base directory where temporary files will be stored
    base_dir = os.path.join(current_cwd, 'temp_dir')  # Base path is './content' under the CWD

    # Create a unique temporary directory under the current working directory
    if 'temp_dir' not in st.session_state:
        temp_base_dir = tempfile.mkdtemp(dir=base_dir)  # Create a temp directory under './content'
        content_dir = os.path.join(temp_base_dir, 'content')  # Create 'content' under the temp directory
        
        # Ensure 'content' directory exists
        os.makedirs(content_dir, exist_ok=True)

        # Store the path in session state
        st.session_state.temp_dir = content_dir

    # Display the path to ensure it's correct
    st.text(st.session_state.temp_dir)

    # Your RedditRetriever setup
    reddit_retriever = RedditRetriever(
        username=st.secrets["REDDIT_USERNAME"],
        secret_key=st.secrets["REDDIT_SECRET_KEY"],
        password=st.secrets["REDDIT_PASSWORD"],
        client_id=st.secrets["REDDIT_CLIENT_ID"],
        output_directory=st.session_state.temp_dir
    )
    stackexchange = StackExchangeRetriever(access_token=st.secrets['STACK_EXCHANGE_ACCESS_TOKEN'],secret_key=st.secrets['STACK_EXCHANGE_SECRET_KEY'])
    query = st.text_input("Enter the input", "")

    # mc = Eurus()

    if st.button("Get Data"):
        try:
            reddit_retriever.get_and_process_data([query])
            st.text("Data Extracted")
            st.code()
            for root,_, files in os.walk(st.session_state.temp_dir):
                for file in files:
                    if file.endswith(".json"):
                        file_path = os.path.join(root, file)

                        # Load and display the JSON content
                        with open(file_path, "r") as f:
                            try:
                                json_content = json.load(f)
                                st.subheader(f"Content of {file}:")
                                st.json(json_content)
                            except json.JSONDecodeError:
                                st.error(f"Error decoding JSON in {file}")
        except Exception as e:
            st.text(e)


main()
