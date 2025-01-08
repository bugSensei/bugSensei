import os
import json
from datetime import datetime
import re
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

class MicrosoftForum:
    def __init__(self, output_directory="/content/output/microsoftforum"):
        # for linux based subsystems(debian)
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--diable-dve-shm-uage')
        self.driver = webdriver.Chrome(options=options)
        self.output_directory = output_directory
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

    def get_data(self, url):
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#Main #PageContent #threadContainer"))
            )
            main = self.driver.find_element(By.CSS_SELECTOR, "#Main #PageContent #threadContainer")
            with open("temp.txt", "w") as f:
                f.write(self.driver.page_source)
            return main
        except Exception as e:
            raise Exception("get_data() : GET() failed") from e

    def get_formatted_date(self, date_string):
        pattern = r"\b\w+[\w\s]*\s+([A-Za-z]+ \d{1,2}, \d{4})"  # Regex for extracting date
        matched = re.search(pattern, date_string)

        if matched:
            datestr = matched.group(1)
            date_object = datetime.strptime(datestr, "%B %d, %Y")
            return str(date_object.date())
        else:
            return date_string

    def process_data(self, main,filename="/processed.json"):
        content = {
            'query': main.find_element(By.CSS_SELECTOR, "#threadMainContent div.questionOnly div.thread-full-message").text,
            'thread_starter_username': main.find_element(By.CSS_SELECTOR, "#threadMainContent div.questionOnly div.message-user-info div.message-user-info-text-and-affiliations").text,
            'last_updated': main.find_element(By.CSS_SELECTOR, "#threadMainContent #threadRightColumnContainer #threadRightSideBar #threadQuestionInfoLastUpdated").text,
            'tags': [tag.text for tag in main.find_elements(By.CSS_SELECTOR, "#threadMainContent #threadRightColumnContainer #threadRightSideBar #threadQuestionInfoAppliesToItems li") if tag.text != '/'],
            'views': int(main.find_element(By.CSS_SELECTOR, "#threadMainContent #threadRightColumnContainer #threadRightSideBar #threadQuestionInfoViews").text.removeprefix("Views ").replace(",", "")),
            'comments_replies': []
        }

        comments = main.find_elements(By.CSS_SELECTOR, "#threadBottomSection div.replies-section #threadReplies #allReplies div.thread-message")

        def get_comment_info(comment):
            reply_action_object = comment.find_elements(By.CSS_SELECTOR, "div.thread-message-content div.thread-message-content-reply-and-message div.thread-message-content-reply-action")
            username = comment.find_element(By.CSS_SELECTOR, "div.thread-message-content-user-info div.message-user-info-text-and-badge div.message-user-info-text-and-affiliations a").text
            comment_date = self.get_formatted_date(comment.find_element(By.CSS_SELECTOR, "div.thread-message-content-user-info div.message-user-info-text-and-badge span.asking-text-asked-on-link button").text)
            comment_data = comment.find_element(By.CSS_SELECTOR, "div.thread-message-content-reply-and-message div.thread-message-content-body div.thread-message-content-body-text").text

            if reply_action_object:
                reply_to_action_text = reply_action_object[0].find_element(By.CSS_SELECTOR, "div.thread-message-content-reply-and-message div.thread-message-content-reply-action button.thread-message-content-reply-action-button").text
                reply_to_user_name, temp_reply_to_user_date = re.search(r'In reply to (.+?)\'s post on (.+)', reply_to_action_text).groups()
                reply_to_user_date = str(datetime.strptime(temp_reply_to_user_date, "%B %d, %Y").date())


                replied_to_content_button = reply_action_object[0].find_element(By.CSS_SELECTOR, "button.thread-message-content-reply-action-button")
                replied_to_content_button.click()
                time.sleep(2)  
                replied_to_content = reply_action_object[0].find_element(By.CSS_SELECTOR, "div.thread-message-content-reply-message").text

                # Match reply to the correct comment
                for comment_entry in content['comments_replies']:
                    if (comment_entry['username'] == reply_to_user_name and 
                        reply_to_user_date in comment_entry['comment_date'] and 
                        replied_to_content.strip().replace(" ", "") == comment_entry['comment_text'].strip().replace(" ", "")):
                        
                        comment_entry['replies'].append({
                            'username': username,
                            'reply_date': comment_date,
                            'reply': comment_data
                        })
                        return  # Exit after adding reply

            else:
                # Add as a standalone comment
                score_elements = comment.find_elements(By.CSS_SELECTOR, "div.thread-message-content-reply-and-message div.thread-message-content-body div.message-voting-container p.vote-message-default")
                score = int(score_elements[0].text.split(" ")[0]) if score_elements and score_elements[0].text else 0

                content['comments_replies'].append({
                    'username': username,
                    'comment_date': comment_date,
                    'comment_text': comment_data,
                    'score': score,
                    'replies': []
                })

        for comment in comments:
            get_comment_info(comment)
            print("Processed a comment...")
        with open(self.output_directory+filename,"w") as f:
          json.dump(content,f,indent=3)

        return content

    def get_and_process_data(self, url,filename="/processed.json"):
        main = self.get_data(url)
        time.sleep(2)
        return self.process_data(main)

    def get_and_process_data_multiple(self,urls):
      for i in range(len(urls)):
        main = self.get_data(urls[i])
        time.sleep(2)
        content = self.process_data(main,filename=f"/{i}.json")
        print(content)
      print()
