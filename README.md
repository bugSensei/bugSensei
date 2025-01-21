# BugSensei

<p align="center">
  <img src="assets/logo.jpeg" alt="Logo" width="200">
</p>

## Overview

Ever felt frustrated with issues you faced with your computer? Be it software or hardware, solving these issues entirely on your own is a tedious process. And when you do call tech support, you are left more frustrated than ever due to  bad customer service and lack of proper technical support.

More than often, solutions to these problems could be found through extensive google search and reading several websites and user manuals. But this is an extremely unpleasant process and often leaves a bad taste, but in this era of LLMs,  one might say why not use ChatGPT? 

But more than often answers related to troubleshooting computer issues  are often generic and not quite specific to the issue in hand.

And so, in bold attempt, we decided to develop BugSensei. 

[![Streamlit Logo](https://raw.githubusercontent.com/streamlit/streamlit/develop/docs/img/streamlit-logo-dark.svg)](https://bugsensei-7arergvxfiffv6rxxtlvqx.streamlit.app/)


### Developed By

- [Anirudh A](https://github.com/AnirudhArrepu)
- [Niranjan M](https://github.com/all-coder)

## Architecture

![alt text](assets/architecture.jpg)

## Agents Overview
  - Web Search Agent
  - Snowflake Agent
  - Decision Agent
  - codeShell
  
<<<<<<< HEAD
  ### Web Search Agent
    - Codenamed as "Eurus", this agent is responsible for extracting data from the most relevant search
     results based off the user's query post query refinement.
    - This agent dynamically enlists bots under its management and retrieve data from websites.
    - The data is then formatted to make LLM ready for contextual information and then dumped 
    into separate folders.
    
  ### Snowflake Agent
    - This agent is tasked with communicating with snowflake and with the other agents 
    - It learns new information from the Web-Search agent and uploads acquired data to its 
    knowledge base
    - It also performs query refinement to ensure better results from cortex-search and web-search
    - It retrieves pertinent data from the knowledge base based on the refined query and
     generates responses using the mistral-large based on the context recieved from the 
     similarity search of the embeddings
=======
  #### Web Search Agent
  - Codenamed as "Eurus", this agent is responsible for extracting data from the most relevant search results based off the user's query post query refinement.
  - This agent dynamically enlists bots under its management and retrieve data from websites.
  - The data is then formatted to make LLM ready for contextual information and then dumped into separate folders.
    
  #### Snowflake Agent
  - This agent is tasked with communicating with snowflake and with the other agents 
  - It learns new information from the Web-Search agent and uploads acquired data to its knowledge base
  - It also performs query refinement to ensure better results from cortex-search and web-search
  - It retrieves pertinent data from the knowledge base based on the refined query and generates responses using the mistral-large based on the context recieved from the similarity search of the embeddings
>>>>>>> 4fad646232f9c949826b4dbcf8cdba2e95379042

  #### Decision Agent
  - It summarises all the generated documents and assigns a relevance score to each of the document based on its relevance to the query and re-ranks the document, the top ranked results are communicated to snowflake agent to update its knowledge base and the top result is used to generate powershell script by the codeshell agent

  #### codeShell
  - This is a fine-tuned Mistral 7b v0.3 whose task is to generate Powershell Scripts(Powershell for now) to resolve the user's issue in an efficient and easy manner.
  - This 4 bit quantized model was fine-tuned using Unsloth's framework which proved to be quite memory and resource efficient for fine-tuning jobs.
  - The model's lora adapters can be downloaded from the attached link below and can be tested with the colab notebook : notebooks -> codeShell_model_testing.ipynb
  

## .env / Secrets.toml

```
REDDIT_USERNAME = 
REDDIT_PASSWORD = 
REDDIT_CLIENT_ID = 
REDDIT_SECRET_KEY = 

STACK_EXCHANGE_ACCESS_TOKEN = 
STACK_EXCHANGE_SECRET_KEY = 

TAVILY_API_KEY =""

SNOWFLAKE_ACCOUNT = ""
SNOWFLAKE_USER = ""
SNOWFLAKE_PASSWORD = ""
SNOWFLAKE_wAREHOUSE = ""
SNOWFLAKE_DATABASE = ""
SNOWFLAKE_SCHEMA = ""
```
