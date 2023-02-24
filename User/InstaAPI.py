import json
from ._creds import Creds 
from ._data import uid 
from ._ig_graph_api import GraphAPI

class user(GraphAPI):

    def __init__(self, mode, arg):
        #mode 0 for access token login and mode 1 for json file login 
        global uid 
        uid += 1 
        if mode == 0:
            self.creds["access_token"] = arg
            accounts = self.get_accounts()
            self.get_ll_token()
            self.creds["accounts"] = accounts 
            self.get_ig_account()
            #saving the creds
            with open("Cache/%d.json" % uid, "w") as file:
                file.write(json.dumps(self.creds, indent=4))
        elif mode == 1:
            uid = arg
            with open("Cache/%d.json" % uid, "r") as file:
                #this is kinda dangerous, what if it's in the wrong format? 
                self.creds = json.load(file)



