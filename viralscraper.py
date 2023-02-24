from User import * 
from Reddit import *
from Publitio import *
import json
import time 
import subprocess
import os

download_limit = 1

def get_actual_ids(batch):
    output = list()
    for publitio_id in batch: 
        if '-' in publitio_id:
            output.append(publitio_id[:-2])
        else:
            output.append(publitio_id)
    return output


def upload(subreddit,max_post,tag,pipelineID):
    # we don't have a lot of control over the number of post... 
    batch_num = max_post // download_limit 
    collector = RedditAPI.API()
    HeisenBone = InstaAPI.user(1,1)

    collector.find_batch(subreddit,218,tag) #the reason why we don't do this is because we don't want to keep finding the batch every single time we need to upload a batch. We save it in batch.json
    for i in range(batch_num): 
        with open("batch_output.json","r") as f:
            batch_output = json.load(f)
            collector.download_reddit_batch(batch_output,pipelineID,i*download_limit) #downloading a new reddit videos batch (this thing is downloading more than 5 ) the second argument needs to be incremented
            # print("finished downloading")
            public_ids, links = PublitioAPI.upload_batch(pipelineID) # publishing those batch to publitio 
            ids = get_actual_ids(public_ids)
            captions = collector.get_titles(ids,batch_output) #get the title of those videos 
            print(captions)
            with open("links.txt","w") as file, open("captions.txt","w") as file2:
                #save the links and captions 
                file.write(" ".join(links))
                file2.write(" ".join(captions))
            HeisenBone.upload_batch(links,captions)
            #clean up, delete all batches and files from publitio 
            print("Cleaning up...")
            clear(pipelineID) 


def clear(pipelineID):
    print(clear_batch(pipelineID))
    print(clear_publitio())

def clear_batch(pipelineID):  
    reels_path = f'media/reels/pipeline_{pipelineID}'
    # get a list of all the files in the folder
    files = os.listdir(reels_path)
    print(files)
    # iterate over the list of files
    for file in files:
        # construct the full path to the file
        file_path = os.path.join(reels_path, file)
        # delete the file
        # run the "sudo" command with the "rm" command and the "-rf" flags as arguments
        # subprocess.run(["sudo", "rm", "-rf", file_path])
        os.remove(file_path)



def clear_publitio(): 
    #this needs improvements too 
    responses = [] 
    failed = []
    files = PublitioAPI.list_files()
    ids = [i['id'] for i in files['files']]
    for id in ids: 
        responses.append(PublitioAPI.delete_file(id))
    for response in responses:
        if not response['success']:
            failed.append(response['message'])
    return failed 


#need to have some sort of system that remembers the post that has already been uploaded 
# should have a system that tells you how many videos actually got uploaded 

# while they're at it, let's think about what to do next... 
# so now that everything is going in hte pipeline, we need to decide how to do things concurrently

# upload("r/Unexpected",1,'top',0)
