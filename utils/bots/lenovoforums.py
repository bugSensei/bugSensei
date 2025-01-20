import os
import json

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver


class LenovoForum:
    def __init__(self, output_directory="./content/output/lenovoforum"):
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=options)

        # ensuring the directory exists
        self.output_directory = output_directory
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

    def __del__(self):
        if self.driver:
            self.driver.quit()

    def get_data(self, url):
        try:
            self.driver.get(url)
            # wait for the page to load
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "body div.main-frame section.app-main div.main-topic-area div.topic-area",
                    )
                )
            )
            main = self.driver.find_element(
                By.CSS_SELECTOR,
                "body div.main-frame section.app-main div.main-topic-area div.topic-area",
            )
            return main
        except Exception as e:
            raise Exception(
                f"LenovoForums : get_data() : webpage retrieval failed! Details: {str(e)}"
            )

    def format_json_to_text(self, data, output_filename):
        output_filepath = self.output_directory + f"/{output_filename}"
        text = f"## Query : {data.get('thread_query')}\n"
        text += f"## Description : {data.get('thread_description')}\n"
        text += f"## Comments\n"

        for i, comment in enumerate(data.get("comments")):
            text += f"  ## Comment {i+1}\n"
            text += f"    Likes : {comment.get('likes')}\n"
            text += f"    Verified Checks : {comment.get('verified_checks')}\n"
            text += f"    {comment.get('description')}\n"

        with open(output_filepath, "w") as f:
            f.write(text)
        f.close()

    def process_data(self, main, filename):
        try:
            comment_posts = main.find_elements(
                By.CSS_SELECTOR, "div.topic-content div.single-post-area"
            )
            thread_starter_post = comment_posts.pop(0)

            thread_starter_username = thread_starter_post.find_element(
                By.CSS_SELECTOR, "div.sp-mark div.user-name-area"
            ).text.split()[0]
            thread_posted_date = thread_starter_post.find_element(
                By.CSS_SELECTOR, "div.sp-mark span.post-date"
            ).text
            thread_query = thread_starter_post.find_element(
                By.CSS_SELECTOR, "div.sp-mark h2.single-post-title"
            ).text
            thread_description = thread_starter_post.find_element(
                By.CSS_SELECTOR, "div.sp-mark div.single-post-content"
            ).text
            thread_verification_stats = thread_starter_post.find_elements(
                By.CSS_SELECTOR, "div.sp-mark div.user-info span.kudo-num"
            )
            thread_likes = int(thread_verification_stats[0].get_attribute("innerHTML"))
            thread_verified_checks = int(
                thread_verification_stats[1].get_attribute("innerHTML")
            )

            comments = []
            for post in comment_posts:
                username = post.find_element(
                    By.CSS_SELECTOR, "div.sp-mark div.user-name-area"
                ).text.split()[0]
                date = post.find_element(
                    By.CSS_SELECTOR, "div.sp-mark span.post-date"
                ).text
                description = post.find_element(
                    By.CSS_SELECTOR, "div.sp-mark div.single-post-content"
                ).text
                verification_stats = post.find_elements(
                    By.CSS_SELECTOR, "div.sp-mark div.user-info span.kudo-num"
                )
                likes = int(verification_stats[0].get_attribute("innerHTML"))
                verified_checks = int(verification_stats[1].get_attribute("innerHTML"))

                comments.append(
                    {
                        "username": username,
                        "date": date,
                        "description": description,
                        "likes": likes,
                        "verified_checks": verified_checks,
                    }
                )

            content = {
                "thread_starter_username": thread_starter_username,
                "thread_posted_date": thread_posted_date,
                "thread_query": thread_query,
                "thread_description": thread_description,
                "thread_likes": thread_likes,
                "thread_verified_checks": thread_verified_checks,
                "comments": comments,
            }

            with open(f"{self.output_directory}/{filename}", "w") as f:
                json.dump(content, f, indent=3)
            print("LenovoForums : Data retrieved and processed successfully")

            return content
        except Exception as e:
            raise Exception(
                f"LenovoForums : process_data() : data processing failed! Details: {str(e)}"
            )

    def get_and_process_data(self, urls):
        if not urls:
            raise Exception("LenovoForum : get_and_process_data() : no URLs are given!")
        try:
            for i, url in enumerate(urls):
                main = self.get_data(url)
                content = self.process_data(main, filename=f"{i}.json")
                self.format_json_to_text(data=content, output_filename=f"{i}.txt")
        except Exception as e:
            raise Exception(
                f"LenovoForum : get_and_process_data() : data extraction failed! Details: {str(e)}"
            )
        
### Example Usage ###
# lenovoforum_retriever = LenovoForum()
# lenovoforum_retriever.get_and_process_data(urls = []) 

