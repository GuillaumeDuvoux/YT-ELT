import requests  
import json
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="./.env" )

 
API_KEY=os.getenv("API_KEY")

max_results=50

CHANNEL="MrBeast"

def get_playlist_id():

    try:

        url=f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL}&key={API_KEY}"

        response=requests.get(url)

        response.raise_for_status()

        data=response.json()

        #print(json.dumps(data,indent=4))



        channel_items=data["items"][0]
        channel_playlist_id=channel_items["contentDetails"]["relatedPlaylists"]["uploads"]
        #print(channel_playlist_id)
        return channel_playlist_id
    
    except requests.exceptions.RequestException as e:
        raise e
    
    
playlist_id=get_playlist_id()
print(playlist_id)

def get_video_id(playlist_id):

    video_ids=[]
    pageToken=None


    base_url=f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={max_results}&playlistId={playlist_id}&key={API_KEY}"

    try:
        while True:
            url=base_url

            if pageToken:
                url+=f"&pageToken={pageToken}"

            response=requests.get(url)

            response.raise_for_status()

            data=response.json()

            for items in data.get('items',[]):
                video_id=items['contentDetails']['videoId']
                video_ids.append(video_id)
            
            pageToken=data.get('nextPageToken')

            if not pageToken:
                break
        return video_ids


    except requests.exceptions.RequestException as e:
        raise e

def extract_video_data(video_ids):

    extracted_data=[]
    def batch_list(video_id_lst,batch_size):
        for video_id in range (0,len(video_id_lst),batch_size):
            yield video_id_lst[video_id: video_id+batch_size]


    try:
        for batch in batch_list(video_ids,max_results): 
            video_id_str=",".join(batch)
            url=f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={video_id_str}&key={API_KEY}"
            response=requests.get(url)
            response.raise_for_status()
            data=response.json()

            for items in data.get("items",[]):
                id=items['id']
                contenDetails=items['contentDetails']
                snippet=items["snippet"]
                statistics=items['statistics']

                video_data={
                    "video_id":id,
                    "title":snippet['title'],
                    "publishedAt":snippet['publishedAt'],
                    "duration":contenDetails['duration'],
                    "view_count":statistics.get("view_count",None),
                    "likeCount":statistics.get("likeCount",None),
                    "commentCount":statistics.get("commentCount",None),
                }

                extracted_data.append(video_data)
        return extracted_data
        



    except requests.exceptions.RequestException as e:
        raise e

if __name__=="__main__":
   playlistId=get_playlist_id()
   video_ids=get_video_id(playlistId)
   extract_video_data(video_ids)

    # print (channel_playlist_id)