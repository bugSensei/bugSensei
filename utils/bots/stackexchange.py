import os
import json
import requests

class StackExchangeRetriever:
    def __init__(self,access_token,secret_key):
        # use .env file for storing the access token and the secret key
        # could also access stackexchange api without access token, but requests are limited
        # with access tokens, request rate limit is upto ~ 10,000/day
        self.access_token = access_token
        self.secret_key = secret_key

        self.base_url = 'https://api.stackexchange.com/2.3'
        self.headers = {'Authorization': f'Bearer {self.access_token}', 'Accept': 'application/json'}
        self.payload_endpoints = ["", "answers", "comments"]

        self.output_directory = "./content/output/stackexchange"
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
    # gets the formatted urls with self.base_url as the prefix and also the updated endpoints based on the self.payload_endpoints
    def get_formatted_url_and_domain_name(self, url, payload=""):
        question_id = url.split("/questions/")[1].split("/")[0]
        domain_name = url.split("//")[1].split("/")[0].replace(".com", "")
        endpoint = f'/questions/{question_id}/{payload}'
        formatted_url = self.base_url + endpoint
        return formatted_url, domain_name

    def get_data(self, url):
        file_name = "raw_data"
        try:
            for i in self.payload_endpoints:
                formatted_url, domain_name = self.get_formatted_url_and_domain_name(url, i)
                params = {'site': domain_name, 'access_token': self.access_token, 'filter': 'withbody', 'key': self.secret_key}
                response = requests.get(formatted_url, headers=self.headers, params=params)
                if response.status_code == 200:
                    if i == "":
                        with open(f"{self.output_directory}/{file_name}_general_info.json", 'w') as f:
                            json.dump(response.json(), f, indent=2)
                    else:
                        with open(f"{self.output_directory}/{file_name}_{i}.json", 'w') as f:
                            json.dump(response.json(), f, indent=2)
                else:
                    raise Exception(f"get_data() : {i} payload endpoint causing error")
        except Exception as e:
            print(e)

    def process_data(self,file_index):
        file_name = "raw_data"

        def extract_general_info(content, data):
            content['thread_starter_name'] = data['items'][0]['owner']['display_name']
            content['thread_starter_id'] = data['items'][0]['owner']['user_id']
            content['query'] = data['items'][0]['title']
            content['description'] = data['items'][0]['body']
            content['view_count'] = data['items'][0]['view_count']
            content['tags'] = data['items'][0]['tags']

        def extract_answers(content, data):
            for item in data['items']:
                answer_post = {
                    'user_name': item['owner']['display_name'],
                    'user_id': item['owner']['user_id'],
                    'reputation': item['owner']['reputation'],
                    'answer_id': item['answer_id'],
                    'answer': item['body'],
                    'score': item['score']
                }
                content.setdefault('answers', []).append(answer_post)

        def extract_comments_replies(content, data):
            replies = {}
            for item in data['items']:
                user_id = item['owner']['account_id']
                if user_id not in replies:
                    replies[user_id] = {
                        'display_name': item['owner']['display_name'],
                        'reputation': item['owner']['reputation'],
                        'accept_rate': item['owner'].get('accept_rate'),
                        'reply_to_user': {},
                        'comments': []
                    }
                if 'reply_to_user' in item:
                    reply_to_user_id = item['reply_to_user']['account_id']
                    replies[user_id]['reply_to_user'].setdefault(reply_to_user_id, {
                        'user_id': reply_to_user_id,
                        'reputation': item['reply_to_user']['reputation'],
                        'display_name': item['reply_to_user']['display_name'],
                        'replies': []
                    })['replies'].append(item['body'])
                else:
                    replies[user_id]['comments'].append(item['body'])
            content['comments'] = replies

        with open(f"{self.output_directory}/{file_name}_general_info.json", 'r') as f:
            data_general_info = json.load(f)
        with open(f"{self.output_directory}/{file_name}_answers.json", 'r') as f:
            data_answers = json.load(f)
        with open(f"{self.output_directory}/{file_name}_comments.json", 'r') as f:
            data_comments_replies = json.load(f)

        content = {}
        extract_general_info(content, data_general_info)
        extract_answers(content, data_answers)
        extract_comments_replies(content, data_comments_replies)

        with open(self.output_directory+f"/{file_index}.json", "w") as f:
            json.dump(content, f, indent=3)
        print("Data has been processed and dumped into processed.json")
        
    def get_and_process_data(self,urls):
      if(len(urls)==0):
        raise Exception("StackExchangeRetriever : get_and_process_data() : urls not given !")
      else:
        try:
          for i in range(len(urls)):
            self.get_data(urls[i])
            self.process_data(file_index=i)
          print("Data has been successfully retrieved and dumped")
        except Exception as e:
          raise Exception("StackExchangeRetriever : get_and_process_data() : retrieval has failed !")
          print(e)

### Example Usage ###
# stackexchange_retriever = StackExchangeRetriever(access_token="",secret_key="") - for more info access the stack exchange api documentation
# urls = [] -  put your urls over here
# stackexchange_retriever.get_and_process_data(urls)