from ._creds import Creds
from ._data import data
import requests
import json
import time 
class GraphAPI(Creds):
    def get_ig_account(self):
        # assuming that the creditials has established
        accounts = self.creds["accounts"]
        for id in accounts:
            url = data['base_url'] + "/%s" % id
            params = {
                "fields": "instagram_business_account",
                "access_token": accounts[id]["page_token"]
            }
            response = requests.get(url, params=params).json()
            accounts[id]["instagram_business_account"] = response["instagram_business_account"]

    # content publishing
    ''''
    feature: 
    1st: create container 
    2nd: publishing content 

    status code 
    content publishing limit 
    '''

    def create_container(self, ig_id, page_token, type, media_url ,caption="", **ext):
        # carousel container is not included 
        url = data["base_url"] + "/%s/media" % ig_id

        if type == "image":
            params = {
                "image_url": media_url,
                "caption": caption,
                "access_token": page_token,
            }
            # include other additional parameters
            for key, value in ext.items():
                params[key] = value
        elif type == "video":
            params = {
                "media_type": "VIDEO",
                "video_url": media_url,
                "caption": caption,
                "access_token": page_token
            }
            for key, value in ext.items():
                params[key] = value
        elif type == "reel":
            params ={ 
                "media_type":"REELS",
                "video_url":media_url,
                "caption":caption,
                "share_to_feed": "true",
                "access_token":page_token
            }
        
        response = requests.post(url, params=params).json()
        # print("RECEIVED ID:")
        # print(response["id"])
        # print()
        # print()
        return response["id"]

    def create_carousel_container(self, ig_id, page_token, caption, children,**ext):
        url = data["base_url"] + "/%s/media" % ig_id
        child_param = ""

        for type,media_url in children:
            child_param += self.create_container(ig_id,page_token,type,media_url) + "%"
        child_param = child_param[:-1] #cut the last %

        params = { 
            "media_type":"CAROUSEL",
            "caption":caption,
            "children":child_param, 
            "access_token":page_token
        }
        #external values addition 
        for key,value in ext.items():
            params[key] = value 
        response = requests.get(url, params).json()
        return response["id"]
        
    def publish_content(self, ig_id, page_token, content_id):
        url = data["base_url"] + f"/{ig_id}/media_publish"
        params = {
            "creation_id": content_id,
            "access_token":page_token
        }
        # print("PUBLISH ID:")
        # print(content_id)
        # print()
        # print()
        response = requests.post(url,params).json() 
        # print(response)
        return response["id"]

    def get_status(self,container_id,page_token):
        #get the current container status 
        url = data["base_url"] + f"/{container_id}"
        params = {
            "fields":"status_code",
            "access_token":page_token
        }
        response = requests.get(url,params).json()
        if response["status_code"] == "ERROR":
            print(response)
        return response["status_code"]


    def upload_reel(self,video_url,caption=""):
        #handle all of the status stuff expired (skip), error (skip), finished (->continue publishing), in progres(loop until you're good), published (skip) 
        #create_container(self, ig_id, page_token, type, media_url ,caption="", **ext)
        id2 = "ERROR"
        for id in self.creds["accounts"]:
            #we need to fix this, this will just go to the last one no?
            account = self.creds["accounts"][id]
            ig_id = account["instagram_business_account"]['id']
            page_token = account['page_token']
        id1 = self.create_container(ig_id,page_token,"reel",video_url,caption) 
        #check if the containe is ready or not 
        status = self.get_status(id1,page_token)
        while status=="IN_PROGRESS":
            print("The reel is in progress, waiting...")
            status = self.get_status(id1,page_token)
            #wait for like 30 seconds 
            time.sleep(3)
        if status == 'FINISHED':
            print("The reel is ready!")
            id2 = self.publish_content(ig_id,page_token,id1)
        else:
            print(status)
        return id2 
    
    def upload_batch(self,links,captions):
        #I think we need caption assembler 
        if len(links) != len(captions):
            print("Links and caption has to be paired up")
        else:
            for i in range(len(links)):
                print(self.upload_reel(links[i],captions[i]))

    def search_hashtag(self,hashtag):
        url = data["base_url"] + "/ig_hashtag_search"
        for id in self.creds["accounts"]:
            #we need to fix this, this will just go to the last one no?
            account = self.creds["accounts"][id]
            ig_id = account["instagram_business_account"]['id']
            page_token = account['page_token']
            params = {
                "user_id": ig_id,
                "q":hashtag,
                "access_token":page_token
            }
            response = requests.get(url,params).json()
            print(response)
            break
        return response

 
