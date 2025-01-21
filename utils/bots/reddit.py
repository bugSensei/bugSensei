import os
import json
import requests


class RedditRetriever:
    def __init__(self, username, password, client_id, secret_key,output_directory="./content/output/reddit/"):
        if (
            username is None
            or password is None
            or client_id is None
            or secret_key is None
        ):
            raise Exception(
                " RedditRetreiver : initialization(init): Enter valid credentials"
            )
        else:
            self.base_url = "https://oauth.reddit.com/"
            self.username = username
            self.password = password
            self.client_id = client_id
            self.client_secret = secret_key

            self.output_directory = output_directory+"/reddit"

            # checking whether the specified directory exists
            if not os.path.exists(self.output_directory):
                os.makedirs(self.output_directory,exist_ok=True)

            # getting the headers; this is the one to be used while making requests to Reddit
            # route the requests via oauth, use self.base_url
            self.headers = self.get_headers()
            if self.headers is None:
                raise Exception("Invalid Headers, check credentials once more")
            else:
                check_status = requests.get(
                    "https://oauth.reddit.com/api/v1/me", headers=self.headers
                )
                if check_status.status_code != 200:
                    raise Exception("Response Status 403")
                else:
                    pass

    # get the final headers that is also used while making requests to the reddit endpoint
    def get_headers(self):
        auth = requests.auth.HTTPBasicAuth(self.client_id, self.client_secret)
        personal_data = {
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
        }
        headers = {"User-Agent": "Reddit-Retriever"}
        res = requests.post(
            "https://www.reddit.com/api/v1/access_token",
            auth=auth,
            data=personal_data,
            headers=headers,
        )
        if res.status_code == 200:
            TOKEN = res.json()["access_token"]
            headers = {**headers, **{"Authorization": f"bearer {TOKEN}"}}
            return headers
        else:
            return None

    # formats the url, replaces www.reddit.com  -> oauth.reddit.com
    def get_formatted_url(self, url):
        path = url.removeprefix("https://www.reddit.com/").removeprefix(
            "https://reddit.com/"
        )
        if not path.startswith("/"):
            path = "/" + path
        return self.base_url + path

    # makes the actual request to the reddit endpoint and dumps the raw json data in a file
    def get_data(self, url):
        formatted_url = self.get_formatted_url(url)
        req = requests.get(formatted_url, headers=self.headers)
        if req.status_code == 200:
            with open(self.output_directory + "reddit.json", "w") as f:
                json.dump(req.json(), f, indent=4)
            return req.json()
        else:
            raise Exception("Data not retrieved")

    # converts json to text
    def format_json_to_text(self, input_json_filepath):
        output_text_file = input_json_filepath.split(".")[0] + ".txt"
        try:
            with open(input_json_filepath, "r", encoding="utf-8") as json_file:
                data = json.load(json_file)

            with open(output_text_file, "w", encoding="utf-8") as text_file:
                title = data.get("query", "No Title")
                description = data.get("description", "No Description")
                text_file.write(f"Title: {title}\n")
                text_file.write(f"Description: {description}\n\n")

                comments = data.get("comments", [])
                for comment in comments:
                    text_file.write(
                        f"Comment: {comment.get('body', 'No body content')}\n"
                    )
                    text_file.write(f"Score: {comment.get('score', 0)}\n")
                    text_file.write(f"Replies:\n")

                    def write_replies(replies, level=1):
                        for reply in replies:
                            indent = "  " * level
                            text_file.write(
                                f"{indent}Reply Body: {reply.get('body', 'No body content')}\n"
                            )
                            text_file.write(
                                f"{indent}Reply Score: {reply.get('score', 0)}\n"
                            )

                            if reply.get("replies"):
                                text_file.write(f"{indent}Nested Replies:\n")
                                write_replies(reply["replies"], level + 1)

                    write_replies(comment.get("replies", []))

                    text_file.write("\n" + "-" * 80 + "\n")
        except Exception as e:
            print(f"Error: {e}")

    # processes the raw data received and extracts only the relevant parameters
    def get_processed_data(
        self, raw_data, max_depth=2, file_name="reddit_processed.json"
    ):
        # max_depth = 2 -> refers to the level of replies to each comment that is to be taken into processed_data
        # a recursive function that extracts comments and replies upto max_depth
        def process_comments(comment_data, current_depth=0):
            if current_depth > max_depth:
                return None
            comment_info = {
                "id": comment_data.get("id"),
                "author": comment_data.get("author"),
                "body": comment_data.get("body"),
                "score": comment_data.get("score", 0),
                "replies": [],
            }

            if comment_data.get("replies"):
                try:
                    # checks whether there are any replies to the comments
                    if isinstance(comment_data["replies"], dict):
                        reply_list = (
                            comment_data["replies"].get("data", {}).get("children", [])
                        )
                    else:
                        reply_list = comment_data["replies"]
                    # loops into every reply in the reply_list, and data is extracted
                    for reply in reply_list:
                        reply_data = (
                            reply.get("data", reply)
                            if isinstance(reply, dict)
                            else reply
                        )
                        nested_reply = process_comments(reply_data, current_depth + 1)
                        if nested_reply:
                            comment_info["replies"].append(nested_reply)
                except Exception as e:
                    print(f"Error processing replies: {e}")
            return comment_info

        # checking whether there are any comments
        if not raw_data or len(raw_data) < 2:
            return {"comments": []}
        # comments retrieved from the raw_data
        comments_data = raw_data[1]["data"]["children"]
        # initializing the processed_comments
        processed_comments = []
        for comment in comments_data:
            comment_data = comment.get("data", comment)
            processed_comment = process_comments(comment_data)
            if processed_comment:
                processed_comments.append(processed_comment)

        # final data dumped onto the .json file
        output_data = {
            "query": raw_data[0]["data"]["children"][0]["data"].get("title", ""),
            "description": raw_data[0]["data"]["children"][0]["data"].get(
                "selftext", ""
            ),
            "comments": processed_comments,
        }
        try:
            with open(self.output_directory + file_name, "w") as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(e)

    ### run this function ###
    def get_and_process_data(self, urls, max_depth=2):  # takes in a urls array.
        if len(urls) == 0:
            raise Exception("No URLs are given !")
        else:
            try:
                for i in range(len(urls)):
                    raw_data = self.get_data(urls[i])
                    self.get_processed_data(
                        raw_data,
                        max_depth,
                        file_name="reddit_processed_" + str(i) + ".json",
                    )
                    self.format_json_to_text(
                        input_json_filepath=self.output_directory + f"{i}.json"
                    )
                    print("RedditRetriever() : Data Retrieved and Processed")
                os.remove(self.output_directory + "reddit.json")
            except Exception as e:
                print(e)


### Example Usage ###
# reddit_retriever = RedditRetriever(username,password,client_id,secret_key)  - for more info access the reddit developer docs.
# urls = [] - put your urls over here
# reddit_retriever.get_and_process_data(urls,max_depth=2) #default is 2.
