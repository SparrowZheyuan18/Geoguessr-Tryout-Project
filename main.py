import json
import asyncio
from tqdm import tqdm
from openai import OpenAI
from retry import retry
# from utils.youtube_transcript import parse_video_id, get_script_from_youtube, merge_transcript, split_transcript
# from utils.location import get_locations, parse_challenge_id
# from utils.images import get_images, combine_images
from configuration import Config


LLM = OpenAI(api_key=Config.MODEL.OPENAI_API_KEY)
model = "gpt-4-turbo"
prompt = "Here is a youtube transcript of a player playing geoguessr, in which he is trying to guess the location based on the current views. The youtuber might or might not starts with prologue, play the game, and might or might not end with a epilogue. Please find useful clues he mentioned when he plays, and return me only the clues (it should be some paraphrased clues separated by commas like xxx brands of cars, court style buildings, driving on the right, etc. don't list points and keep clues concise). Instead of using the player's point of view, state the clues in the scene in a neutral tone without mentioning the player) in the transcripts, and exclude the other parts. The clues should not showing the correctness of the final results. The transcript is as follows:\n"

player = "rainbolttwo"

image_path = f"data/images/images_{player}"
full_data_path = f"data/splited_data/{player}_split.jsonl"
processed_data_path = f"data/clues_1/clues_{player}.jsonl"


def load_data(path):
    with open(path, 'r') as f:
        if path.endswith(".jsonl"):
            data = [json.loads(line) for line in f]
        else:
            data = json.load(f)
    return data


def dump_jsonl(objects, file_name):
    out_file = open(file_name, "w")
    for obj in objects:
        tmp = out_file.write(json.dumps(obj, ensure_ascii=False) + "\n")
        out_file.flush()


def get_data_of_videos():
    data = load_data(data_path)
    
    for videos in tqdm(data):
        youtube_url = videos["youtube_url"]
        challenge_url = videos["challenge_url"]
        data_item = {
            "youtube_url": youtube_url,
            "challenge_url": challenge_url
        }

        # get youtube transcript
        video_id = parse_video_id(youtube_url)
        try:
            transcript_list = get_script_from_youtube(video_id)
            data_item["transcript"] = merge_transcript(transcript_list)
        except:
            print("no transcript available")
            continue

        challenge_id = parse_challenge_id(challenge_url)

        # get locations
        data_item["locations"] = asyncio.run(get_locations(challenge_id))

        # get images
        for i, item in enumerate(data_item["locations"]):
            print(f"Getting images for round {i+1}")
            location = f"{item['lat']}, {item['lng']}"
            try:
                get_images(location, id=challenge_id, path=image_path, round=i+1)
            # if image does not exist, pass
            except:
                data_item["image_not_available"] = [i+1]
            try:
                combine_images(image_path, challenge_id, round=i+1)
            except:
                data_item["image_not_available"] = [i+1]
        
        data_item["images_path"] = f"{image_path}/{challenge_id}"

        yield data_item

        # with open(full_data_path, 'w') as f:
        #     json.dump(full_data, f, indent=4, ensure_ascii=False)


def get_processed_data():
    data = load_data(full_data_path)
    for item in tqdm(data[:]):
        transcript = item["transcript"]
        locations = item["locations"]
        images_path = item["images_path"]
        # print("calling gpt to split transcript")
        # transcript_list = split_transcript(transcript, paraphrase=False)
        print("calling gpt to paraphrased transcript")
        paraphrased_transcript_list = split_transcript(transcript, paraphrase=True)
        # there are data that misses images
        if "image_not_available" in item:
            not_available_list = item["image_not_available"]
        else:
            not_available_list = []
        for i in range(5):
            if i+1 in not_available_list:
                continue
            yield {
                "youtube_url": item["youtube_url"],
                "challenge_url": item["challenge_url"],
                # "transcript": transcript_list[i],
                "paraphrased_transcript": paraphrased_transcript_list[i]["transcript"],
                "is_correct": paraphrased_transcript_list[i]["is_correct"],
                "location": locations[i],
                "image_path": f"{images_path}/{i+1}/combined.jpg"
            }


def get_clues():
    data = load_data(full_data_path)
    for item in tqdm(data[:]):
        transcript = item["split_transcript"]
        location = item["location"]
        images_path = item["image_path"]
        # print("calling gpt to split transcript")
        # transcript_list = split_transcript(transcript, paraphrase=False)
        print("calling gpt to paraphrased transcripts")
        @retry(tries=5, delay=10)           
        def call_gpt():
            response = LLM.chat.completions.create(
                model=model,
                messages=[
                    {'role': 'user', 'content': [{'type': 'text', 'text': prompt+transcript}]}
                ],
            )
            return response
        response = call_gpt()
        content = response.choices[0].message.content
        # paraphrased_transcript_list = split_transcript(transcript, paraphrase=True)
        # there are data that misses images
        # if "image_not_available" in item:
        #     not_available_list = item["image_not_available"]
        # else:
        #     not_available_list = []
        # for i in range(5):
        #     if i+1 in not_available_list:
        #         continue
        yield {
            "youtube_url": item["youtube_url"],
            "challenge_url": item["challenge_url"],
            # "transcript": transcript_list[i],
            "clues": content,
            # "is_correct": paraphrased_transcript_list[i]["is_correct"],
            "image_path": images_path,
            "location": location
        }
        

if __name__ == "__main__":
    # dump_jsonl(get_data_of_videos(), full_data_path)
    # dump_jsonl(get_processed_data(), processed_data_path)
    dump_jsonl(get_clues(), processed_data_path)

