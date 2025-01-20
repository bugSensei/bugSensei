# ToDo
# remove usernames and passwords from the .py file
# create .env imports throughout the workspace(entire project)
# need to write data formatters .json -> .txt(for contextual info) to make it LLM Ready.
# need to add tavily or serp api as a fall back, in case the google search using selenium automation fails

# need to add the following
# AmdCommunity()
# general imports
import os
import json
import re
import concurrent.futures
import streamlit as st

# from dotenv import load_dotenv


from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from tavily import TavilyClient

# importing from utils
from utils.bots.reddit import RedditRetriever
from utils.bots.stackexchange import StackExchangeRetriever
from utils.bots.tomsforum import TomsForumRunner
from utils.bots.microsoft_forum import MicrosoftForum
from utils.bots.amd_community import AmdCommunity
from utils.bots.lenovoforums import LenovoForum

# load_dotenv()


# The entire web retreival pipeline is handled via the Eurus Object.
# extracts relevant search results based on the query and enlists bots based on demand.
class Eurus:
    def __init__(self, output_directory="./output/"):
        ## Driver Options - for linux based subsystems
        # self.options = webdriver.ChromeOptions()
        # self.options.add_argument("--no-sandbox")
        # self.options.add_argument("--headless")
        # self.options.add_argument("--disable-gpu")
        # self.options.add_argument("--diable-dve-shm-uage")
        # self.driver = webdriver.Chrome(options=self.options)

        # self.output_directory = output_directory

        ## this is where element of the "search" class is going to be stored
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

    # automates google search using selenium
    # def google_search(self, search_query):
    #     self.driver.get("https://google.com")
    #     WebDriverWait(self.driver, 10).until(
    #         EC.presence_of_element_located((By.CLASS_NAME, "gLFyf"))
    #     )
    #     search_class = self.driver.find_element(By.CLASS_NAME, "gLFyf")
    #     search_class.clear()
    #     search_class.send_keys(search_query + Keys.ENTER)
    #     search_class = self.driver.find_element(By.ID, "search")
    #     return search_class

    # def extract_elements(self, search_class):
    #     xpath_query = ".//div[@class='ULSxyf']//div[@class='MjjYud'] | .//div[@class='MjjYud'] | .//div[@class='hlcw0c']//div[@class='MjjYud']"
    #     elements = search_class.find_elements(By.XPATH, xpath_query)
    #     return elements

    # # extracts headers and links and formats them into a dictionary
    # def extract_headers_and_links(self, elements, file_name="gsearch.json"):
    #     result = []
    #     full_file_path = self.output_directory + file_name

    #     for element in elements:
    #         element_data = {}

    #         try:
    #             element_data["snippet"] = element.text
    #         except Exception:
    #             element_data["snippet"] = None

    #         try:
    #             h3_tag = element.find_element(By.XPATH, ".//h3")
    #             element_data["header"] = h3_tag.text
    #         except Exception:
    #             element_data["header"] = None

    #         try:
    #             a_tag = element.find_element(By.XPATH, ".//a")
    #             element_data["url"] = a_tag.get_attribute("href")
    #         except Exception:
    #             element_data["url"] = None

    #         if element_data["header"] and element_data["header"]:
    #             result.append(element_data)

    #     with open(full_file_path, "w", encoding="utf-8") as f:
    #         json.dump(result, f, ensure_ascii=False, indent=4)

    #     print(f"Search Results Dumped to {full_file_path}")
    #     return result

    def getTavily(self, query):
        tavily_client = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])
        response = tavily_client.search(query, max_results=10)
        with open("./output/gsearch.json", "w") as f:
            json.dump(response["results"], f, indent=3)
        return response["results"]

    # direct method to extract the search results and dump it onto a json file
    def get_search_results(self, search_query):
        search_class = self.google_search(search_query)
        search_elements = self.extract_elements(search_class)
        result = self.extract_headers_and_links(search_elements)
        return result

    # maps the url on the basis of the domain names and we use this to allocate the bots on basis of this.
    def get_mapped_urls(self, search_results):
        # bunch of regex functions to check the domain names, so as to allocate bots.
        is_answers_microsoft = lambda url: bool(
            re.search(r"answers\.microsoft\.com", url)
        )
        is_stack_exchange = lambda url: bool(
            re.search(r"(superuser\.com|stackoverflow\.com)", url)
        )
        is_reddit = lambda url: bool(re.search(r"reddit\.com", url))
        is_tomsforum = lambda url: bool(
            re.search(r"(forums\.tomsguide\.com|forums\.tomshardware\.com)", url)
        )
        is_amdforum = lambda url: bool(re.search(r"(community\.amd\.com)", url))
        is_lenovoforum = lambda url: bool(re.search(r"(forums\.lenovo\.com)", url))

        # this dict contains the list of the urls mapped to its respective domains
        mapped_urls = {
            "answers_microsoft": [],
            "tomsforum": [],
            "stackexchange": [],
            "reddit": [],
            "amdforum": [],
            "lenovoforum": [],
            "other": [],
        }

        for i in search_results:
            if is_answers_microsoft(i["url"]):
                mapped_urls["answers_microsoft"].append(i["url"])
            elif is_stack_exchange(i["url"]):
                mapped_urls["stackexchange"].append(i["url"])
            elif is_reddit(i["url"]):
                mapped_urls["reddit"].append(i["url"])
            elif is_tomsforum(i["url"]):
                mapped_urls["tomsforum"].append(i["url"])
            elif is_amdforum(i["url"]):
                mapped_urls["amdforum"].append(i["url"])
            elif is_lenovoforum(i["url"]):
                mapped_urls["lenovoforum"].append(i["url"])
            else:
                mapped_urls["other"].append(i["url"])

        return mapped_urls

    # allocates and run entities on the basis of the mapped_urls object.
    def generate_and_run_entities(self, mapped_urls):
        # initializing retrievers, so as to ensure global access
        (
            stackexchange_retriever,
            reddit_retriever,
            tomsforum_retriever,
            answers_microsoft_retriever,
            amdforum_retriever,
            lenovoforum_retriever,
        ) = (None, None, None, None, None, None)

        if len(mapped_urls) == 0:
            raise Exception("Eurus : generate_entities() : No URLs are given !")
        else:
            # assign retriever objects based on the availability of the urls in mapped_urls
            if len(mapped_urls.get("stackexchange", [])) != 0:
                stackexchange_retriever = StackExchangeRetriever(
                    access_token=st.secrets["STACK_EXCHANGE_ACCESS_TOKEN"],
                    secret_key=st.secrets["STACK_EXCHANGE_SECRET_KEY"],
                )
            if len(mapped_urls.get("reddit", [])) != 0:
                reddit_retriever = RedditRetriever(
                    username=st.secrets["REDDIT_USERNAME"],
                    password=st.secrets["REDDIT_PASSWORD"],
                    secret_key=st.secrets["REDDIT_SECRET_KEY"],

                    client_id=st.secrets["REDDIT_CLIENT_ID"]
                )
            if len(mapped_urls.get("tomsforum", [])) != 0:
                tomsforum_retriever = TomsForumRunner()
            if len(mapped_urls["answers_microsoft"]) != 0:
                answers_microsoft_retriever = MicrosoftForum()
            if len(mapped_urls["amdforum"]) != 0:
                amdforum_retriever = AmdCommunity()
            if len(mapped_urls["lenovoforum"]) != 0:
                lenovoforum_retriever = LenovoForum()

            # a list containing all the functions to be executed concurrently
            # tasks = []
            try:
                if stackexchange_retriever:
                    stackexchange_retriever.get_and_process_data(
                        mapped_urls["stackexchange"]
                    )
            except Exception as e:
                print("StackExchange Failed to retrieve Data")
            try:
                if reddit_retriever:
                    reddit_retriever.get_and_process_data(mapped_urls["reddit"])
            except Exception as e:
                print("Reddit Failed to retrieve data")
            try:
                if tomsforum_retriever:
                    tomsforum_retriever.get_and_process_data(mapped_urls["tomsforum"])
            except Exception as e:
                print("Tom's Hardware Failed to extract data")
            try:
                if answers_microsoft_retriever:
                    answers_microsoft_retriever.get_and_process_data_multiple(
                        mapped_urls["answers_microsoft"]
                    )
            except Exception as e:
                print("Microsoft Community Failed to Extract Data")
            try:
                if amdforum_retriever:
                    amdforum_retriever.get_and_process_data(mapped_urls["amdforum"])
            except Exception as e:
                print("Amd Forum failed to extract data")
            try:
                if lenovoforum_retriever:
                    lenovoforum_retriever.get_and_process_data(mapped_urls["lenovoforum"])
            except Exception as e:
                print("LenovoForums failed to extract data!")

            # # running all retrieval processes simulataneously
            # try:
            #     with concurrent.futures.ThreadPoolExecutor() as executor:
            #         results = executor.map(lambda f: f(), tasks)
            # except Exception as e:
            #     raise Exception("Eurus : generate_entities() : retrieval failed !")
            #     print(e)

    def get_extracted_results(self, search_query):
        try:
            try:
                # search_results = self.get_search_results(search_query)
                search_results = self.getTavily(search_query)
            except Exception as e:
                print("get_search_results failed, switching to getTavily:", e)
            mapped_urls = self.get_mapped_urls(search_results)
            self.generate_and_run_entities(mapped_urls)
            print("Relevant data retrieved and dumped into respective folders")
        except Exception as e:
            raise Exception("Eurus : get_extracted_results() : extraction failed!")
            print(e)

    # def __del__(self):
    #     self.driver.quit()


### Example Usage ###
# ws = Eurus() - initializes the web driver and creates directory for dumping the relevant files.
# ws.get_extracted_results("amd driver not showing up in the task manager")
