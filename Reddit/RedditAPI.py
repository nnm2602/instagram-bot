import requests 
import json
import time 
import os 
import subprocess
from .data import data,download_limit

class API():
    headers = { 
            "User-Agent":"MyAPI/0.0.1"
        }
    auth = requests.auth.HTTPBasicAuth(data["client_id"],data["app_secret"])

    def __init__(self): 
        if os.path.exists("Reddit_headers.json"):
            print("loading the state") 
            self.load_state()
            print("Testing the api...")
            if not self.get_posts('r/TikTokCringe','hot',limit=1): 
                print("key failed, updating keys...")
                self.get_access_token()
            else:
                print("API testing successful")
        else: 
            print("getting the access token")
            self.get_access_token()

    def get_access_token(self):
        load = { 
            "grant_type":"password",
            "username":data["username"],
            "password":data["password"]
        }
        url = data['base_url'] + "/api/v1/access_token"
        response = requests.post(url=url,auth=self.auth,data=load,headers=self.headers).json() 
        self.headers["Authorization"] = f'bearer {response["access_token"]}'
        #update the headers cache associated
        with open("Reddit_headers.json","w") as file:
            file.write(json.dumps(self.headers,indent=4))
        return response["access_token"]

    
    def get_info(self):
        url = data["base_url"] + 'api/v1/me'
        response = requests.get(url=url,auth=self.auth,headers=self.headers)
        status = response.status_code 
        if status == 400:
            self.get_access_token() 
            response = requests.get(url=url,headers=self.headers)
            status = response.status_code 
        if status == 200:
            return response.json()
        return "ERROR"
    
    def load_state(self):
        with open("Reddit_headers.json") as file:
            self.headers = json.load(file)

    def process_response(self,response):
        try:
            response = response.json() 
        except:
            with open("reddit_response.html","w") as file:
                file.write(response.text)
                print("The response is likely an html file, please see reddit_response.html for details")
                response = False 
        return response

    def search_subreddit_name(self,name,exact="false", include_over_18="true", include_unadvertisiable="true"):
        url = data["base_url"] + "api/search_reddit_names"
        load = { 
            "exact": exact,
            "include_over_18":include_over_18,
            "include_unadvertisiable":include_unadvertisiable,
            "query":name
        }
        response = requests.get(url=url,data=load,auth=self.auth,headers=self.headers)
        response = self.process_response(response)
        return response 

    def get_posts(self,subreddit,tag,limit=25, before=None, after=None):
        #before and after to paginate 
        url = data["oauth_url"] + f'{subreddit}/{tag}/'
        params = {
            "limit":limit
        }
        if before != None:
            params["before"] = before
        if after != None:
            params["after"] = after
        response = requests.get(url=url,headers=self.headers,params=params)
        response= self.process_response(response)
        return response 

    def find_batch(self,subreddit,count,tag):
        #find (count) number of post on a subreddit with the requirements given 
        #what happen if we ask for 200 posts? (it will only ever give us 100, we will have to calculate ourselves)
        #count // 100, count % 100 (the floor and the remainder) 
        output = list()
        hundred_batch = count // 100
        remainder = count % 100 
        after_tag = None 
        before_tag = None 
        stop = False 
        #or should I use null instead 
        while hundred_batch != 0: 
            response = self.get_posts(subreddit,tag,100, before=before_tag, after=after_tag)
            #format response will return a list of items with necessarily information 
            output = output + self.format_response(response) #join the table together
            after_tag = response['data']['after']
            if after_tag == "null":
                stop = True 
                break 
            hundred_batch = hundred_batch - 1 
        if not stop:
            response = self.get_posts(subreddit,tag, remainder, before=before_tag, after=after_tag)
        #debug purposes 
        # print(f'The size of the output is: {len(output)}')
        # print("The first few samples are: ")
        # print(output[0])
        # print("-----------------------------")
        # print(output[1])
        # print("------------------------------")
        # print(output[2])
        # print("------------------------------")
        # print(f'There are in total: {len(output)}/{count} video files.')
        with open("batch_output.json","w") as file:
            file.write(json.dumps(output))
        return output 

    def format_response(self,response):     
        output = list() 
        print(response)
        posts = response['data']['children']
        for post in posts: 
            with open("post.json","w") as file:
                file.write(json.dumps(post))
            if post['data']['is_video'] == True:
                print(post['data'])
                duration = post['data']['secure_media']['reddit_video']['duration']
                width = post['data']['secure_media']['reddit_video']['width']
                height = post['data']['secure_media']['reddit_video']['height']
                ratio = width/height
                if duration < 60 and abs(ratio-9/16) <= 0.1 * 9/16:
                    #only get the video in if it's around the same aspect ratio. No more than 10% deviation
                    post_info = {
                        "title": post['data']['title'],
                        "upvotes": post['data']['ups'],
                        "num_comments": post['data']['num_comments'],
                        "id": post['data']['id'],
                        "fullname":post['data']['name'],
                        "video_link":post['data']['secure_media']['reddit_video']['fallback_url'],
                        "audio_link":post['data']['url_overridden_by_dest'] + "/DASH_audio.mp4",
                        "permalink":post['data']['permalink'],
                        "link_flair_text":post['data']['link_flair_text']
                    }
                    output.append(post_info)
                else:
                    with open("failed.txt","a") as file:
                        file.write(f'height: {height}, width: {width}, duration: {duration}\n')
                        
        return output 
        

    def download_reddit_batch(self,batch, pipelineID, starting_point = 0):
        # start from some index and download the maximum number of videos set by download limits from then onwards 
        reels_path = "./media/reels/"
        for item in batch[starting_point:starting_point+download_limit]:
            batch_path = reels_path + f'pipeline_{pipelineID}/'; 
            #download the video and the audio 
            video = requests.get(url=item["video_link"],headers=self.headers)
            audio = requests.get(url=item["audio_link"],headers=self.headers)
            #create the batch folder 
            try:
                os.makedirs(batch_path)
            except:
                pass
            #save the files 
            with open(batch_path + f'{item["id"]}_video.mp4', "wb") as video_file,open(batch_path + f'{item["id"]}_audio.mp4',"wb") as audio_file:
                video_file.write(video.content)
                audio_file.write(audio.content)

            subprocess.call(['ffmpeg','-i',batch_path + f'{item["id"]}_video.mp4','-i',batch_path + f'{item["id"]}_audio.mp4','-map','0:v','-map','1:a','-c:v','copy',batch_path + f'{item["id"]}.mp4'])
            subprocess.call(['rm',batch_path + f'{item["id"]}_video.mp4',batch_path + f'{item["id"]}_audio.mp4'])

    def get_titles(self,ids, batch):
        titles = list() 
        found = False
        for id in ids:
            for post in batch:
                if id == post['id']:
                    titles.append(post['title'])
                    found = True 
                    break 
            if not found:
                titles.append("")
            else:
                found = False
        return titles 
                

    def get_comments(self):
        #remember to fix this function 
        url = data['oauth_url'] + f'r/TikTokCringe/comments/yorpbg'
        response = requests.get(url=url,headers=self.headers).json()
        return response 



# HeisenBone = API() 
# # # HeisenBone.load_state()
# HeisenBone.get_access_token()
# # # time.sleep(3)
# print(HeisenBone.get_info())
# print(HeisenBone.find_batch("r/TikTokCringe",218,"hot"))
# # with open("batch_output.json", "r") as file:
# #     batch = json.load(file)
# #     HeisenBone.download_reddit_batch(batch)

'''
Do we really need a folder that specifically catered to a batch? 
yes because we want to output as much video as we can by streamline it concurrently 
so like we can assure that every video is ready before we upload it
'''


'''
find_content(subreddit,count,requirement(tag,numberOfLikes,...))
'''
'''
What is an behavior, it's like a move on a chess board or any game that the computer could choose to move.
it's composed of:
    - what it is, when to execute it, where to upload it, how it is being upload, what to do after being uploaded 
    - how do you even train a model like that to learn what to do, that's insane 
    - can you use gpt 3 to reason? that seems a bit far fetched 
'''




