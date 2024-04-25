import re
import json
from youtube_transcript_api import YouTubeTranscriptApi 
from configuration import LLM
from retry import retry
  

divide_prompt = "Here is a youtube transcript of a player playing geoguessr, in which he is trying to guess the location based on the current views. There are totally five rounds. The youtuber starts with prologue, 5 rounds of games, and epilogue. Please split the scripts of 5 rounds of games, and return me only a python list of the 5 round transcripts with punctuation, and exclude the other parts. Also, the player sometimes get the answer correct, or get it wrong. You should determine it based on his word. Your should only return a list of python dict like [{'transcript': '...', 'is_correct': True}, {...}] (Use double quotation marks instead). The transcript is as follows:\n"
paraphrase_prompt = "Here is a youtube transcript of a player playing geoguessr, in which he is trying to guess the location based on the current views. There are totally five rounds. The youtuber starts with prologue, 5 rounds of games, and epilogue. Please split the scripts of 5 rounds of games, find useful clues in each round, and return me only a python list of the paraphrased clues (like xxx brands of cars, court style buildings, etc. Instead of using the player's point of view, state the clues in the scene in a neutral tone) in each round in the transcripts with punctuation, and exclude the other parts. The clues should not showing the correctness of the final results. Also, the player sometimes get the answer correct, or get it wrong. You should determine it based on his word. Your should only return a list of python dict without '\n', like [{'transcript': clues in the first round, 'is_correct': True}, {...}] (Use double quotation marks instead). The transcript is as follows:\n"

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

@retry(tries=5, delay=2)
def get_script_from_youtube(id):
    video_id = id
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return transcript


def merge_transcript(transcript_list):
    transcript = ""
    for i in transcript_list:
        transcript += i['text'] + " "
    return transcript


def json_parser(text):
    # parse the json part inside the text
    # print(text)
    start = text.find("[")
    end = text.find("]") + 1
    clean_data = ' '.join(text[start:end].split()).replace("False", "false").replace("True", "true")
    data = json.loads(clean_data)
    return data


@retry(tries=5, delay=2)
def split_transcript(transcript, paraphrase=False):
    if paraphrase:
        prompt = paraphrase_prompt
    else:
        prompt = divide_prompt

    model = "gpt-4-1106"
    
    def call_gpt():
        response = LLM.chat.completions.create(
            model=model,
            messages=[
                {'role': 'user', 'content': [{'type': 'text', 'text': prompt+transcript}]}
            ]
        )
        return response
    response = call_gpt()
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