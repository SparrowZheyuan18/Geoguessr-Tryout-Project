import re
from youtube_transcript_api import YouTubeTranscriptApi 
  

divide_prompt = "Here is a youtube transcript of a player playing geoguessr, in which he is trying to guess the location based on the current views. There are totally five rounds. The youtuber starts with prologue, 5 rounds of games, and epilogue. Please split the scripts of 5 rounds of games, and return me only a python list of the 5 round transcripts with punctuation, and exclude the other parts. Your return should only include the list. The transcript is as follows:"
paraphrase_prompt = "Here is a youtube transcript of a player playing geoguessr, in which he is trying to guess the location based on the current views. There are totally five rounds. The youtuber starts with prologue, 5 rounds of games, and epilogue. Please split the scripts of 5 rounds of games, find useful clues in which he plays the game, and return me only a python list of the paraphrased clues in each round in the transcripts with punctuation, and exclude the other parts. Your return should only include the list that looks like ['clue in the first round', 'clue in the second round', ... ]. The transcript is as follows:"

def parse_video_id(url):
    # There are 6 patterns of YouTube video URL.
    patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',  
        r'(?:https?://)?youtu\.be/([a-zA-Z0-9_-]{11})',                        
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',     
        r'(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})',         
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?.*?v=([a-zA-Z0-9_-]{11})', 
        r'(?:https?://)?(?:www\.)?youtube\.com/playlist\?.*?v=([a-zA-Z0-9_-]{11})' 
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)  
    return "Invalid URL!"


def get_script_from_youtube(url):
    video_id = url
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return transcript


def merge_transcript(transcript_list):
    transscript = ""
    for i in transcript_list:
        transscript += i['text'] + " "
    return transscript


if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=t98r-YV6LnQ"
    video_id = parse_video_id(video_url)
    print(video_id)
    transcript_list = get_script_from_youtube(video_id)
    transcript = merge_transcript(transcript_list)
    print(len(transcript))