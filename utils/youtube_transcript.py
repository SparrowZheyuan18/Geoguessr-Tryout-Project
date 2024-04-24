import re
import sys
from youtube_transcript_api import YouTubeTranscriptApi 
from configuration import LLM
  

divide_prompt = "Here is a youtube transcript of a player playing geoguessr, in which he is trying to guess the location based on the current views. There are totally five rounds. The youtuber starts with prologue, 5 rounds of games, and epilogue. Please split the scripts of 5 rounds of games, and return me only a python list of the 5 round transcripts with punctuation, and exclude the other parts. Also, the youtuber sometimes get the answer correct, or get it wrong. You should determine it based on his word. Your should only return a json, like [{'transcript': '...', 'is_correct': True}, {...}]. The transcript is as follows:\n"
paraphrase_prompt = "Here is a youtube transcript of a player playing geoguessr, in which he is trying to guess the location based on the current views. There are totally five rounds. The youtuber starts with prologue, 5 rounds of games, and epilogue. Please split the scripts of 5 rounds of games, find useful clues in which he plays the game, and return me only a python list of the paraphrased clues in each round in the transcripts with punctuation, and exclude the other parts. The clues should be neutral and not showing the correctness of the final results. Also, the youtuber sometimes get the answer correct, or get it wrong. You should determine it based on his word. Your should only return a json without '\n', like [{'transcript': clue in the first round, 'is_correct': True}, {...}]. The transcript is as follows:\n"

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
    transcript = ""
    for i in transcript_list:
        transcript += i['text'] + " "
    return transcript


def json_parser(text):
    # parse the json part inside the text
    start = text.find("[")
    end = text.find("]") + 1
    return text[start:end]


def split_transcript(transcript, paraphrase=False):
    if paraphrase:
        prompt = paraphrase_prompt
    else:
        prompt = divide_prompt

    model = "gpt-4-1106"
    response = LLM.chat.completions.create(
        model=model,
        messages=[
            {'role': 'user', 'content': [{'type': 'text', 'text': prompt+transcript}]}
        ]
    )
    content = response.choices[0].message.content
    content = json_parser(content)
    return content


if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=t98r-YV6LnQ"
    video_id = parse_video_id(video_url)
    print(video_id)
    transcript_list = get_script_from_youtube(video_id)
    transcript = merge_transcript(transcript_list)
    print(len(transcript))
    a = split_transcript(transcript, paraphrase=True)
    print(a)