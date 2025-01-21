import os
import json
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

class AmdCommunity:
  def __init__(self,output_directory):
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--diable-dve-shm-uage')
    self.driver = webdriver.Chrome(options=options)

    self.output_directory = output_directory+"/amdcommunity/"
    os.makedirs(self.output_directory,exist_ok=True)
  
  def get_data(self,url):
    self.driver.get(url)
    # waiting for the page to load
    WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,"body center div.container-parsys div.cmp-container__content")))
    body = self.driver.find_element(By.CSS_SELECTOR,"body center div.container-parsys div.cmp-container__content")
    main = body.find_element(By.CSS_SELECTOR,"div.container-parsys div.cmp-container__content div.lia-content div.lia-quilt-row-main")
    return main  # the html structure which contains all the relevant elements.
  
  def process_data(self,main):
    # extracting info about the thread starter
    thread_starter = main.find_element(By.CSS_SELECTOR,"div.lia-quilt-column-main-content")
    thread_starter_username = thread_starter.find_element(By.CSS_SELECTOR,"div.lia-quilt-row-message-header").text.split()[0]
    thread_starter_query = thread_starter.find_element(By.CSS_SELECTOR,"div.threaded-message-list div.lia-quilt-row-message-subject").text
    thread_starter_description = thread_starter.find_element(By.CSS_SELECTOR,"div.lia-quilt-row-message-body").text
     # formatting the date 
    posted_date = thread_starter.find_element(By.CSS_SELECTOR,"div.lia-quilt-row-message-post-times").text
    date_object = datetime.strptime(posted_date, "%m-%d-%Y %I:%M %p")
    thread_posted_date = str(date_object.date())
    # extracting the list of comments
    comments = main.find_elements(By.CSS_SELECTOR,"#threadeddetailmessagelist div.threaded-detail-message-list div.lia-threaded-detail-display-message-view")
    formatted_comments = []
    for index, i in enumerate(comments):
        username = i.find_element(By.CSS_SELECTOR, "div.lia-quilt-row-message-header").text
        message_date = i.find_element(By.CSS_SELECTOR, "div.lia-quilt-row-message-post-times").text
        date_object = datetime.strptime(message_date, "%m-%d-%Y %I:%M %p")
        comment_text = i.find_element(By.CSS_SELECTOR, "div.lia-quilt-row-message-body").text
        score = int(i.find_element(By.CSS_SELECTOR,"div.KudosButton").text.split()[0])
        
        comment_info = {
            'username': username.split('\n')[0],
            'comment_date': str(date_object.date()),
            'comment_text': comment_text,
            'score': score,
            'replies': []
        }
        # goes upto level-02 for retrieving comments, could implement a recursive function to dynamically retrieve replies to comments 
        try:
            if(len(i.find_elements(By.CSS_SELECTOR,"div.lia-thread-level-00"))!=0):
              formatted_comments.append(comment_info)
            elif(len(i.find_elements(By.CSS_SELECTOR,"div.lia-thread-level-01"))!=0):
              formatted_comments[-1]['replies'].append(comment_info)
            elif(len(i.find_elements(By.CSS_SELECTOR, "div.lia-thread-level-02")) != 0):
              formatted_comments[-1]['replies'][-1]['replies'].append(comment_info)
        except Exception as e:
          raise Exception("Retrieval Error!")
          print(e)
          continue
      
    content = {
        "thread_starter_username": thread_starter_username,
        "thread_starter_query": thread_starter_query,
        "thread_starter_description": thread_starter_description,
        "thread_posted_date": thread_posted_date,
        "comment": formatted_comments,
      }
    
    return content

  def get_and_process_data(self, urls):
      for i, url in enumerate(urls):
          try:
              main_content = self.get_data(url)
              content = self.process_data(main_content)
              filepath = self.output_directory + f"{i}.json"
              with open(filepath, "w") as f:
                  json.dump(content, f, indent=3)
              print(f"Data for URL {url} saved to {filepath}")
          except Exception as e:
              print(f"Error processing URL {url}: {e}")
      
      print("AmdCommunity: get_and_process_data() : Data retrieved and dumped successfully!")
  def __del__(self):
    self.driver.quit()


### Example Usage ###
# amd_community_retriever = AmdCommunity() - initializing the AmdCommunity Object
# urls = [] - put your urls over here
# amd_community_retriever.get_and_process_data(urls)