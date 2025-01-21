# BugSensei

<p align="center">
  <img src="assets/logo.jpeg" alt="Logo" width="200">
</p>

## Architecture

![alt text](assets/architecture.jpg)

## Agents Overview
  - Web Search Agent
  - Snowflake Agent
  - Decision Agent
  - codeShell
  
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

  ### Decision Agent
    - It summarises all the generated documents and assigns a relevance score to each of the document based on its relevance to the query and re-ranks the document, the top ranked results are communicated to snowflake agent to update its knowledge base and the top result is used to generate powershell script by the codeshell agent

  ### codeShell
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
