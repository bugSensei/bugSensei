import os
import json
import streamlit as st

from utils import eurus
# unsummarized files under /content/output/summarize -- refer utils/snowflake_agent.py
def web_search(search_query):
    try:
        wt = eurus.Eurus()
        wt.get_extracted_results(search_query)   
    except Exception as e:
        print("Web Extraction Failed !",e)



#snowflake retrieval

#decision agent

#upload to snowflake 
