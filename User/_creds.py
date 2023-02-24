import requests
import json
from ._data import data, uid

class Creds:
    creds = dict()
    def get_access_token(self):
            if "access_token" in self.creds:
                return self.creds["access_token"]
            else:
                #get access token
                pass

    def get_ll_token(self): 
        '''
        "https://graph.facebook.com/{graph-api-version}/oauth/access_token?  
        grant_type=fb_exchange_token&          
        client_id={app-id}&
        client_secret={app-secret}&
        fb_exchange_token={your-access-token}" 
        '''
        if "ll_token" not in self.creds or self.is_expired(self.creds["ll_token"]):
            self.ll_token_request()
            # if "code" not in self.creds:
            #     self.get_code() 
        return self.creds["ll_token"]

    def ll_token_request(self):
        #the pure ll_token_request
        '''
        "https://graph.facebook.com/{graph-api-version}/oauth/access_token?  
        grant_type=fb_exchange_token&          
        client_id={app-id}&
        client_secret={app-secret}&
        fb_exchange_token={your-access-token}" 

        "https://graph.facebook.com/{graph-api-version}/oauth/access_token?   
        code={code-for-your-client}&
        client_id={app-id}&
        redirect_uri={app-redirect-uri}&
        machine_id= {your-client-machine-id}"
        '''

        url = data["base_url"] + "/oauth/access_token"
        if "code" in self.creds:
            #get the ll_token with the code
            params= {
                "code":self.creds["code"],
                "client_id":data["app_id"],
                "redirect_uri":"http://thereisnosite.com/"
            }
            response = requests.get(url,params).json()
        else:
            #get the ll_token without the code 
            params = { 
                "grant_type":"fb_exchange_token",
                "client_id":data["app_id"],
                "client_secret":data["app_secret"],
                "fb_exchange_token":self.get_access_token()
            }
            response = requests.get(url,params).json()
        self.creds["ll_token"] = response["access_token"]
        # self.creds["ll_expiry"] = response["expires_in"]
        return response["access_token"] 

        
    def get_code(self): 
        #get the user's code 
        '''
        "https://graph.facebook.com/{graph-api-version}/oauth/client_code?             
        client_id={app-id}&
        client_secret={app-secret}&
        redirect_uri={app-redirect-uri}&
        access_token={long-lived-user-access-token}" 
        '''
        url = data["base_url"] + "/oauth/client_code"
        params = {
            "client_id":data["app_id"],
            "client_secret":data["app_secret"],
            "redirect_uri":"http://thereisnosite.com/", 
            "access_token":self.creds["ll_token"]
        }
        response = requests.get(url,params).json()

        self.creds["code"] = response["code"]
        return response["code"]

    def debug_token(self,input_token):
        url = data["base_url"] + "/debug_token"
        params = { 
            "input_token":input_token,
            "access_token":self.get_access_token()
        }
        response = requests.get(url,params).json()
        return response

    def is_expired(self,input_token):
        response = self.debug_token(input_token)
        return response["data"]["is_valid"]

    def get_accounts(self):
        '''
        https://graph.facebook.com/{your-user-id}/accounts?access_token={user-access-token}
        '''
        output = dict() 
        url = data['base_url'] + "/me/accounts"
        params = {
            "access_token":self.get_ll_token()
        }
        response = requests.get(url,params).json() 
        for page in response["data"]:
            output[page["id"]] = {
                "page_token":page["access_token"]
                }
        #saving accounts 
        return output 
