import os
import json
import streamlit as st
from utils import Snowflake

from utils import eurus
# unsummarized files under /content/output/summarize -- refer utils/snowflake_agent.py
def web_search(search_query):
    try:
        wt = eurus.Eurus()
        wt.get_extracted_results(search_query)   
    except Exception as e:
        print("Web Extraction Failed !",e)

def snowflake_retrieval(snowflake, search_query):
    snowflake.get_answer_from_rag(search_query)
    return snowflake.get_answer_from_rag(search_query)


def query_refiner(snowflake, search_query):
    refined_query = snowflake.query_refiner(search_query)
    return refined_query

snowflake = Snowflake()

#snowflake retrieval

#decision agent

#upload to snowflake 
