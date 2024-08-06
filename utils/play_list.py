import requests
import json
import re
import time
from pytube import Playlist, YouTube
from bs4 import BeautifulSoup
from requests.exceptions import SSLError


play_list = 'https://www.youtube.com/playlist?list=PL_japiE6QKWq-MCBz_wNr92yw0-HWeY2v'
play_list = 'https://www.youtube.com/playlist?list=PL9NsJvmALD3whYFwBQ0ByskPwkcpCFyzz'
play_list = 'https://www.youtube.com/playlist?list=PL9NsJvmALD3zeZ3xbPgj3_hDwexMwJF0_'
play_list = 'https://www.youtube.com/playlist?list=PL8U3zlooRj_kAoZeV6_ijpkp2tMWgQHav'
play_list = 'https://www.youtube.com/playlist?list=PLoJ2Qo3fReLlmPWTzTTTH3t7ahCWvuOdM'
play_list = 'https://www.youtube.com/playlist?list=PL8AAM81D0gVrIXj_zifdzUJ1DeJwrjcY4'
output_file = 'urls.json'
output_file = 'urls_rainbolttwo_2.json'
output_file = 'urls_rainbolttwo_1.json'
output_file = 'urls_geopeter.json'
output_file = 'urls_geocatto.json'
output_file = 'urls_geogasm.json'


def fetch_playlist_details(playlist_url):
    playlist = Playlist(playlist_url)
    print(f'Fetching videos for playlist: {playlist.title}')
    data_list = []
    for i, video in enumerate(playlist.videos):
        print(f'Fetching video {i+1}/{len(playlist.videos)}')
        print(video.watch_url)  # Prints each video URL
        # the description pytube returns is None, so I have to fetch it from the video page
        video_url = video.watch_url
        video_url = video.watch_url + "&list=" + playlist_url.split("list=")[1] + "&index=" + str(i+1)
        challenge_url = fetch_video_description_links(video_url)
        data_list.append({
            'youtube_url': video_url,
            'challenge_url': challenge_url
        })
        # print(data_list)
    return data_list


def save_to_json(data_list, output_file):
    with open(output_file, 'w') as f:
        json.dump(data_list, f, indent=4)
    print(f'Fetched {len(data_list)} videos')
    return


def fetch_video_description_links(video_url, max_retries=5):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive'
    }
    attempt = 0
    while attempt < max_retries:
        try:
            response = requests.get(video_url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # print(soup)
                script_tag = soup.find('script', text=re.compile('ytInitialPlayerResponse'))
                if script_tag:
                    try:
                        # get video description
                        json_text = re.search(r'var ytInitialPlayerResponse = ({.*?});', script_tag.string).group(1)
                        data = json.loads(json_text)
                        description = data.get('videoDetails', {}).get('shortDescription', '')
                        base_url = "geoguessr.com/challenge/"
                        # special_base_url = "TODAY'S CHALLENGE (PLAY BEFORE WATCHING):\nhttps://www.geoguessr.com/challenge/"
                        if base_url in description:
                            pattern = rf'{re.escape(base_url)}[a-zA-Z0-9]{{16}}'
                            description = re.search(pattern, description).group(0)
                        else:
                            return None
                        pattern = rf'{re.escape(base_url)}[a-zA-Z0-9]{{16}}'
                        match = re.search(pattern, description) 
                        # print(match)
                        if match:
                            result = match.group(0)
                            result = f"https://www.{result}"
                            print(result)
                            return result
                        else:
                            result = None
                        return result
                    except Exception as e:
                        print(f'Failed to fetch video description: {e}')
                        print("script_tag:", script_tag)
                        return None
            else:
                attempt += 1
                print(f"Attempt {attempt}: Request failed with status {response.status_code}, retrying...")
                time.sleep(1)
        except SSLError as e:
            print(f"Attempt {attempt}: {e}, retrying...")
            attempt += 1
            time.sleep(1)
    else:
        print("request failed")
        return None
    

# def fetch_video_description_links(video_url, max_retries=5):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive'
    }
    attempt = 0
    while attempt < max_retries:
        try:
            response = requests.get(video_url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # print(soup)
                script_tag = soup.find('script', text=re.compile('ytInitialPlayerResponse'))
                if script_tag:
                    try:
                        # get video description
                        json_text = re.search(r'var ytInitialPlayerResponse = ({.*?});', script_tag.string).group(1)
                        data = json.loads(json_text)
                        description = data.get('videoDetails', {}).get('shortDescription', '')
                        base_url = "geoguessr.com/challenge/"
                        pattern = rf'{re.escape(base_url)}[a-zA-Z0-9]{{16}}'
                        matches = re.findall(pattern, description)                    
                        # print(match)
                        if matches:
                            result = [f"https://www.{match}" for match in matches]
                            print(result)
                            return result
                        else:
                            result = None
                        return result
                    except Exception as e:
                        print(f'Failed to fetch video description: {e}')
                        print("script_tag:", script_tag)
                        return None
            else:
                attempt += 1
                print(f"Attempt {attempt}: Request failed with status {response.status_code}, retrying...")
                time.sleep(1)
        except SSLError as e:
            print(f"Attempt {attempt}: {e}, retrying...")
            attempt += 1
            time.sleep(1)
    else:
        print("request failed")
        return None


if __name__ == "__main__":
    start_time = time.time()
    print(f'Fetching videos from playlist: {play_list}')
    data_list = fetch_playlist_details(play_list)
    save_to_json(data_list, output_file)
    print(f'Execution time: {time.time() - start_time} seconds')
