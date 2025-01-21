import os
import streamlit as st
from mistralai import Mistral
import sys
import json
import uuid
import shutil

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
    # does not have a trailing slash at the end
def generate_temp_dir(): 
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    # st.text(f"Temporary ID: {st.session_state.session_id}")
    current_dir = os.getcwd()
    temp_path = current_dir+f"/{st.session_state.session_id}"
    os.makedirs(temp_path,exist_ok=True)
    # st.session_state.temp_dir = temp_path
    st.text(f"Temporary ID:{temp_path}")
    return temp_path
# def destroy_temp_dir():
#     if "temp_dir" in st.session_state and os.path.exists(st.session_state.temp_dir):
#         shutil.rmtree(st.session_state.temp_dir)
# st.session_state.on_session_end
def main():
    st.title("Testing Eurus")
    temp_path = generate_temp_dir()
    # Your RedditRetriever setup
    # reddit_retriever = RedditRetriever(
    #     username=st.secrets["REDDIT_USERNAME"],
    #     secret_key=st.secrets["REDDIT_SECRET_KEY"],
    #     password=st.secrets["REDDIT_PASSWORD"],
    #     client_id=st.secrets["REDDIT_CLIENT_ID"],
    #     output_directory=temp_path,
    # )
    # stackexchange = StackExchangeRetriever(access_token=st.secrets['STACK_EXCHANGE_ACCESS_TOKEN'],secret_key=st.secrets['STACK_EXCHANGE_SECRET_KEY'])
    query = st.text_input("Enter the input", "")

    mc = Eurus(output_directory=temp_path)
    if st.button("Get Data"):
            try:
                gsearch = None
                mc.get_extracted_results(query)
                st.text("Data extracted")
                try:
                    with open(f"{temp_path}/gsearch.json", "r") as f:
                        gsearch = json.load(f)
                    st.json(gsearch)
                except Exception as e:
                    st.text("gsearch does not exist")
                # with open(f"{temp_path}/tomsforum/0.json") as f:
                #     st.json(json.load(f))
                root_directory = temp_path+"/"

                # Walk through the directory
                for dirpath, dirnames, filenames in os.walk(root_directory):
                    print(f"Checking {dirpath}...")
                    for filename in filenames:
                        print(f"Found file: {filename}")
                        if filename.endswith('.txt'):
                            file_path = os.path.join(dirpath, filename)
                            print(f"Processing file: {file_path}")
                            try:
                                with open(file_path, 'r', encoding='utf-8') as file:
                                    content = json.load(file)
                                    with st.expander(f"File: {file_path}"):
                                        st.json(content)
                            except json.JSONDecodeError:
                                st.error(f"Invalid JSON format in file: {file_path}")
                            except Exception as e:
                                st.error(f"Error reading file {file_path}: {e}")
             
            except Exception as e:
                st.text(e)


main()
