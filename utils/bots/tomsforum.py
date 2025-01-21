import os
import scrapy
import json
from multiprocessing import Process, Queue
import scrapy.crawler as crawler
from twisted.internet import reactor


class TomsForum(scrapy.Spider):
    name = "TomsForum"
    allowed_domains = ["forums.tomsguide.com", "forums.tomshardware.com"]

    def __init__(
        self,
        file_index,
        start_url,
        output_directory="./content/output/tomsforum/",
        *args,
        **kwargs,
    ):
        super(TomsForum, self).__init__(*args, **kwargs)
        self.start_urls = [start_url]
        self.file_index = file_index
        self.output_directory = output_directory

    def format_json_to_text(self, json_file_path, text_file_path):
        try:
            with open(json_file_path, "r") as json_file:
                data = json.load(json_file)

            with open(text_file_path, "w") as text_file:
                text_file.write(f"## Thread Starter Query\n{data['query']}\n\n")
                text_file.write("## Description\n")
                text_file.write(f"{data['description']}\n\n")
                text_file.write("## Thread Starter Comments\n")
                for comment in data.get("thread_starter_comments", []):
                    text_file.write(f"- {comment}\n")
                text_file.write("\n")
                text_file.write("## User Comments\n")
                for comment in data.get("user_comments", []):
                    text_file.write(f"- {comment}\n")

            # print(f"converted JSON to text: {text_file_path}")

        except Exception as e:
            print(f"An error occurred: {e}")

    def parse(self, response):
        content = {}
        main_content = response.css("div.p-body-inner")
        inner_content = main_content.css("div.p-body-pageContent")

        query = main_content.css("div.p-body-header h1.p-title-value::text").get()
        query_description = inner_content.css(
            "div.block--messages article.message--thfeature_firstPost div.message-cell--main div.message-content div.bbWrapper::text"
        ).getall()
        concat_query_description = " ".join(query_description).strip()

        content["query"] = query.strip() if query else "No query found"
        content["description"] = concat_query_description

        thread_starter_comments = inner_content.css(
            "div.block--messages div.js-replyNewMessageContainer article.message-threadStarterPost"
        )
        user_comments = inner_content.css(
            "div.block--messages div.js-replyNewMessageContainer article.message--post"
        )

        content["thread_starter_comments"] = []
        content["user_comments"] = []

        for i in thread_starter_comments:
            comments = i.css(
                "div.message-inner div.message-cell--main div.js-messageContent div.bbWrapper::text"
            ).getall()
            concat_comments = " ".join(comments).strip()
            content["thread_starter_comments"].append(concat_comments)

        for j in user_comments:
            comments = j.css(
                "div.message-inner div.message-cell--main div.js-messageContent div.bbWrapper::text"
            ).getall()
            concat_comments = " ".join(comments).strip()
            content["user_comments"].append(concat_comments)

        # dumping data into json format
        file_path = self.output_directory + f"{self.file_index}.json"
        text_file_path = self.output_directory + f"{self.file_index}.txt"
        with open(file_path, "w") as f:
            json.dump(content, f, indent=4)
        self.format_json_to_text(file_path,text_file_path) # formatting json into text files for making it LLM Ready

        yield content


class TomsForumRunner:
    def __init__(self, output_directory):
        self.output_directory = output_directory+"/tomsforum/"
        os.makedirs(self.output_directory,exist_ok=True)

    def run_spider(self, spider, **kwargs):
        def f(q, spider, kwargs):
            try:
                runner = crawler.CrawlerRunner()
                deferred = runner.crawl(spider, **kwargs)
                deferred.addBoth(lambda _: reactor.stop())
                reactor.run()
                q.put(None)
            except Exception as e:
                q.put(e)

        q = Queue()
        p = Process(target=f, args=(q, spider, kwargs))
        p.start()
        result = q.get()
        p.join()

        if result is not None:
            raise result

    def get_and_process_data(self, urls=[]):
        if len(urls) == 0:
            raise Exception(
                "TomsForumRunner : get_and_process_data() : No URLs are given !"
            )
        else:
            try:
                for i in range(len(urls)):
                    self.run_spider(TomsForum, file_index=i, start_url=urls[i])
                print(
                    "TomsForumRunner : get_and_process_data() : Data Retrieved and Processed"
                )
                print(self.output_directory)
            except Exception as e:
                raise Exception(
                    "TomsForumRunner : get_and_process_data() : failed to retrieve data"
                )
                print(e)


### Example Usage ###
# urls = []  -  Put your urls over here
# tomsforum_bot = TomsForumRunner()
# tomsforum_bot.get_and_process_data(urls)
