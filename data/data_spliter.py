from openai import OpenAI
import json
from retry import retry
from tqdm import tqdm
import re


full_data_path = "data/full_data.jsonl"
splited_full_data_path = "data/splited_full_data2.jsonl"

client = OpenAI(
    api_key='sk-KgGO5KcXA8bcdLs2618fF4Ba831c4a718a5414Ba7802D503',
    base_url="https://yeysai.com/v1/",
)


def call_gpt(model, prompt, visual=False, url=None):
    if visual:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {'role': 'user', 'content': [{'type': 'text', 'text': prompt}, {'type': 'image_url', 'image_url': {"url": url}}]}
            ],
            max_tokens=4000
        )
        return response
    response = client.chat.completions.create(
        model=model,
        messages=[
            {'role': 'user', 'content': [{'type': 'text', 'text': prompt}]}
        ],
        max_tokens=4000
    )
    return response  


def load_data(path):
    with open(path, 'r') as f:
        data = [json.loads(line) for line in f]
    return data


def dump_jsonl(objects, file_name):
    out_file = open(file_name, "w")
    for obj in objects:
        tmp = out_file.write(json.dumps(obj, ensure_ascii=False) + "\n")
        out_file.flush()


# def result_parser(text):
#     start = text.find("```") + 1
#     end = text.find("```")
#     data = eval('[' + text[start:end] + ']')
#     return data


def result_parser(text):
    pattern = r'```python(.*?)```'
    match = re.search(pattern, text, re.DOTALL)
    
    if match:
        list_str = match.group(1).strip()
        try:
            return eval(list_str)
        except Exception as e:
            print(f"Error parsing list: {e}")
            return None
    else:
        print("No list found in the text.")
        return None
    

# @retry(tries=5, delay=10)
def split_transcripts():
    split_prompt = "Here is a youtube transcript of a player playing geoguessr, in which he is trying to guess the location based on the current views. There are totally five rounds. The youtuber starts with prologue, 5 rounds of games, and epilogue. You should identify when he ends the last round (usually he gets a points for that) and starts a new round. Please split the scripts of 5 rounds of games, and return me only a python list of the 5 round transcripts with punctuation, and exclude the other parts. Your should only return a list with form like ['part1', 'part2', ...] (Use double quotation marks instead). You should not paraphrase the transcripts. The transcript is as follows:\n"
    model = "gpt-4o"
    data = load_data(full_data_path)
    for item in tqdm(data[18:]):
        transcript = item["transcript"]
        prompt = split_prompt + transcript
        response = call_gpt(model, prompt, visual=False, url=None)
        content = response.choices[0].message.content
        print(content)
        content = result_parser(content)
        if len(content) != 5:
            print("Error in splitting the transcript")
            return
        for i in range(5):
            yield {
                "youtube_url": item["youtube_url"],
                "challenge_url": item["challenge_url"],
                "transcript": content[i],
                "location": item["locations"][i],
                "image_path": item["images_path"] + f"/{i+1}",
            }


# @retry(tries=5, delay=10)
# def split_transcripts_multiround():
#     model = "gpt-4o-mini"
#     data = load_data(full_data_path)
#     for item in tqdm(data):
#         transcript = item["transcript"]
#         split_prompt = "Here is a youtube transcript of a player playing geoguessr, in which he is trying to guess the location based on the current views. There are totally five rounds. The youtuber starts with prologue, 5 rounds of games, and epilogue. Please split the scripts of 5 rounds of games, and return me only a python list of the 5 round transcripts with punctuation, and exclude the other parts. Your should only return a list of python dict like ['part1', 'part2', ...] (Use double quotation marks instead). You should not paraphrase the transcripts. The transcript is as follows:\n"
#         prompt = split_prompt + transcript
#         response = call_gpt(model, prompt, visual=False, url=None)
#         content = response.choices[0].message.content
#         content = result_parser(content)
#         for i in range(5):
#             yield {
#                 "youtube_url": item["youtube_url"],
#                 "challenge_url": item["challenge_url"],
#                 "transcript": content[i],
#                 "location": item["locations"][i],
#                 "image_path": item["images_path"] + f"/{i+1}",
#             }



if __name__ == "__main__":
    dump_jsonl(split_transcripts(), splited_full_data_path)