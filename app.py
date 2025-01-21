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
from backend.server import snowflake_retrieval,rank_documents,upload_files_to_snowflake,get_user_friendly_responses,get_powershell_code
from utils.snowflake_agent import Snowflake

sys.path.append(".")  # necessary for importing files
st.title("BugSensei")
index=0
# st.set_page_config(page_title="BugSensei",layout="wide")

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


def generate_temp_dir(): 
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    # st.text(f"Temporary ID: {st.session_state.session_id}")
    current_dir = os.getcwd()
    temp_path = current_dir+f"/{st.session_state.session_id}"
    os.makedirs(temp_path,exist_ok=True)
    # st.session_state.temp_dir = temp_path
    # st.text(f"Temporary ID:{temp_path}")
    return temp_path


def generate_responses(query):
        
    temp_path = generate_temp_dir()
    eurus = Eurus(output_directory=temp_path)
    snowflake = Snowflake()

    # query = st.text_input("Enter the input", "")

    #mc = Eurus(output_directory=temp_path)
    try:
        # st.text("rag")
        rag_retreival = snowflake_retrieval(snowflake,query)
        # st.text(rag_retreival)
        # web results are exeucted
        # st.text("web search")
        eurus.get_extracted_results(query)
        root_directory = temp_path+"/"
        # Walk through the directory
        text_file_paths = []
        for dirpath, dirnames, filenames in os.walk(root_directory):
            print(f"Checking {dirpath}...")
            for filename in filenames:
                print(f"Found file: {filename}")
                if filename.endswith('.txt'):
                    file_path = os.path.join(dirpath, filename)
                    text_file_paths.append(file_path)
                    print(f"Processing file: {file_path}")
                    # try:
                    #     with open(file_path, 'r', encoding='utf-8') as file:
                    #         content = file.read()
                    #         with st.expander(f"File: {file_path}"):
                    #             st.text(content)
                    # except Exception as e:
                    #     st.error(f"Error reading file {file_path}: {e}")
        # st.text(text_file_paths)
        # print(text_file_paths)
        snowflake.summarise(file_paths=text_file_paths,temp_path=temp_path)
        # st.text("summarized texts")
        summarize_folder_path = f"{temp_path}/summarize"
        # for filename in os.listdir(summarize_folder_path):
        #     file_path = os.path.join(summarize_folder_path, filename)
        #     print(file_path)
        #     if filename.endswith(".txt") and os.path.isfile(file_path):
        #         with open(file_path, "r") as file:
        #             content = file.read()
        #             with st.expander(f"File:{file_path}"):
        #                 st.text(content)
        # st.text("ranked documents")
        with open(f"{summarize_folder_path}/rag.txt","w") as f:
            f.write(rag_retreival)
        reranked_file_path,result = rank_documents(snowflake=snowflake,query=query,summarize_folder_path=summarize_folder_path,temp_path=temp_path)
        # st.text(result)
        # st.text("Final Responses")
        final_responses = get_user_friendly_responses(snowflake,result[0:2])
        # for i in final_responses:
        #     st.text(i)
        upload_files_to_snowflake(snowflake=snowflake,texts=result)
        code = get_powershell_code(snowflake=snowflake,query=final_responses[0])
        final_responses.append(code)
        return final_responses
        # st.text("files uploaded to snowflake")
    except Exception as e:
        st.text(e)


if 'messages' not in st.session_state:
    st.session_state['messages'] = []


# update the interface with the previous messages
for message in st.session_state['messages']:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# create the chat interface
if prompt := st.chat_input("Enter your query"):
    # Add user's input to session messages
    st.session_state['messages'].append({"role": "user", "content": prompt})
    with st.chat_message('user'):
        st.markdown(prompt)

    # Get two separate responses from the model using the generate_response function
    with st.spinner():
        response1, response2, code = generate_responses(prompt)
    with st.chat_message('assistant'):
        st.markdown(response1)
        st.session_state['response_1'] = response1
    with st.chat_message('assistant'):
        st.markdown(response2)

    with st.modal("Take Action"):
        st.code(code, language="powershell")

    # if st.button("Take Action"):
    #     snowflake_two = Snowflake()
    #     with st.spinner():
    #         response = get_powershell_code(snowflake=snowflake_two,query=response1)
    #     st.code(response,language="powershell")

    
    # Add both responses to session messages
    st.session_state['messages'].append({"role": "assistant", "content": response1})
    st.session_state['messages'].append({"role": "assistant", "content": response2})




    # handle message overflow based on the model size