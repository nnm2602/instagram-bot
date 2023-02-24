from publitio import PublitioAPI
import os
from . import data 
import json
import time 
import requests 
api = PublitioAPI(key=data.key,secret=data.secret)


def publish_batch(pipelineID):
    output = dict() 
    current_directory = os.path.join(data.media_directory,f'pipeline_{pipelineID}')
    for filename in os.listdir(current_directory):
        with open(os.path.join(current_directory,filename),"rb") as video:
            response = api.create_file(file=video,id=filename)
            filename = response['title'] + "." + response['extension']
            if response["width"] < 1080 or response['height'] < 1920:
                #we already have this line here 
                api.transformed(filename,w=1080,h=1920)
            output[response['id']] = response['public_id']
            print(response["public_id"] + " successfully uploaded!")
    return output

def show_file(id):
    return api.show_file(id)

def list_versions(id):
    return api.list_versions(id)

def create_version(id, height, width):
    return api.create_version(id,extension="mp4",h=height,w=width)

def transformed(filename,height,width):
    return api.transformed(filename,h=height,w=width)

def list_files(offset=1):
    return api.list_files(offset=offset)

def delete_file(id):
    return api.delete_file(id)

def get_version_ids(private_ids,h=1920,w=1080):
    version_ids = list() 
    for id in private_ids: 
        versions = api.list_versions(id)["versions"]
        if versions[-1]["options"] == f'h_{h},w_{w}':
            #check the last one first because it's likely 
            version_ids.append(versions[-1]["id"]) 
        else:
            for version in versions: 
                #check everything else if it's not the last one 
                if version["options"] == f'h_{h},w_{w}':
                    version_ids.append(version["id"]) 
    return version_ids 

def get_batch_links(version_ids):
    total_length = len(version_ids)
    links = dict()  #this will contain our final output 
    updated_list = list(version_ids) #this is a deep copy of the list of version ids 
    failed = 0 #keep track of how many videos have failed to process
    while updated_list:
        #while there are still items in the list 
        for version in version_ids: 
            #go through every single ids 
            info = api.show_version(version)
            status = info['status'] 
            if status == "creating":
                #if it's still in progress then move on to the next one 
                break 
            else:   
                with open("status.txt",'a') as file:
                    file.write(status)
                # if it finished processing or failed then update the other list and store our url 
                links[info['file_id']] = info['url']
                updated_list.remove(version)
                if status == "failed":
                    print(version + " failed to process")
                    failed += 1 
        version_ids = updated_list #update the current list 
        time.sleep(2) #only go through the update cycle every 2 seconds (avoid spamming the server)
    if failed == 0:
        print("All of the videos are successfuly processed")
    else:
        print(f'{failed}/{total_length} videos failed to processed')
    return links 

def upload_batch(pipelineID):
    pri_to_pub = publish_batch(pipelineID)
    version_ids = get_version_ids(pri_to_pub.keys())
    pri_to_links = get_batch_links(version_ids)
    public_ids = [pri_to_pub[private_id] for private_id in pri_to_links.keys()]
    links = [link for link in pri_to_links.values()]
    for link in links:
        #pre-request the link for it to work (idk why)
        print(f'preshot executed for {link}')
        requests.get(link)
    return (public_ids,links)



