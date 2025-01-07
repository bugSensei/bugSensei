import os
import scrapy
import json
from multiprocessing import Process, Queue
import scrapy.crawler as crawler
from twisted.internet import reactor

class TomsForum(scrapy.Spider):
    name = "TomsForum"
    allowed_domains = ["forums.tomsguide.com", "forums.tomshardware.com"]

    def __init__(self,file_index, start_url,output_directory="/content/output/tomsforum/", *args, **kwargs):
        super(TomsForum, self).__init__(*args, **kwargs)
        self.start_urls = [start_url]
        self.file_index = file_index
        self.output_directory = output_directory

    def parse(self, response):
        content = {}
        main_content = response.css("div.p-body-inner")
        inner_content = main_content.css("div.p-body-pageContent")

        query = main_content.css("div.p-body-header h1.p-title-value::text").get()
        query_description = inner_content.css(
            "div.block--messages article.message--thfeature_firstPost div.message-cell--main div.message-content div.bbWrapper::text"
        ).getall()
        concat_query_description = " ".join(query_description).strip()

        content['query'] = query.strip() if query else 'No query found'
        content['description'] = concat_query_description

        thread_starter_comments = inner_content.css(
            "div.block--messages div.js-replyNewMessageContainer article.message-threadStarterPost"
        )
        user_comments = inner_content.css(
            "div.block--messages div.js-replyNewMessageContainer article.message--post"
        )

        content['thread_starter_comments'] = [] 
        content['user_comments'] = []

        for i in thread_starter_comments:
            comments = i.css(
                "div.message-inner div.message-cell--main div.js-messageContent div.bbWrapper::text"
            ).getall()
            concat_comments = " ".join(comments).strip()
            content['thread_starter_comments'].append(concat_comments)

        for j in user_comments:
            comments = j.css(
                "div.message-inner div.message-cell--main div.js-messageContent div.bbWrapper::text"
            ).getall()
            concat_comments = " ".join(comments).strip()
            content['user_comments'].append(concat_comments)
        
        # dumping data into json format
        file_path = self.output_directory+f"{self.file_index}.json"
        with open(file_path, 'w') as f:
            json.dump(content, f, indent=4)

        yield content


class TomsForumRunner:
  def __init__(self,output_directory = "/content/output/tomsforum/"):
    self.output_directory = output_directory
    if not os.path.exists(self.output_directory):
      os.makedirs(self.output_directory)

  def run_spider(self,spider, **kwargs):
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
  def get_and_process_data(self,urls=[]):
    if(len(urls)==0):
      raise Exception("TomsForumRunner : get_and_process_data() : No URLs are given !")
    else:
      try:
        for i in range(len(urls)):
          self.run_spider(TomsForum,file_index=i,start_url = urls[i])
        print("TomsForumRunner : get_and_process_data() : Data Retrieved and Processed")
      except Exception as e:
        raise Exception("TomsForumRunner : get_and_process_data() : failed to retrieve data")
        print(e)

### Example Usage ###
# urls = []  -  Put your urls over here
# tomsforum_bot = TomsForumRunner()
# tomsforum_bot.get_and_process_data(urls)