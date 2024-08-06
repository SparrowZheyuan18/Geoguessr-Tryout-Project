import json
import asyncio
from tqdm import tqdm
from utils.youtube_transcript import parse_video_id, get_script_from_youtube, merge_transcript, split_transcript
from utils.location import get_locations, parse_challenge_id
from utils.images import get_images, combine_images
from configuration import Config, client
from retry import retry


data_path = "data/urls_geopeter.json"
image_path = "data/images_geopeter"
full_data_path = "data/full_data_geopeter.jsonl"
full_data_path = "data/full_data_geopeter2.jsonl"
processed_data_path = "data/processed_data_geopeter.jsonl"


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
    
    for videos in tqdm(data[124:]):
        youtube_url = videos["youtube_url"]
        challenge_url = videos["challenge_url"]
        data_item = {
            "youtube_url": youtube_url,
            "challenge_url": challenge_url,
        }

        # get youtube transcript
        video_id = parse_video_id(youtube_url)
        try:
            transcript_list = get_script_from_youtube(video_id)
            data_item["transcript"] = merge_transcript(transcript_list)
        except:
            print("no transcript available")
            continue

        locations = []
        img_path = []

        for i, challenge_url_item in enumerate(challenge_url):
            print(f"loading game {i+1}")
            challenge_id = parse_challenge_id(challenge_url_item)

            # get locations
            print(challenge_id)
            location = asyncio.run(get_locations(challenge_id))
            locations.append(location)
            print(location)

            # get images
            for i, item in enumerate(location):
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
            
            img_path.append(f"{image_path}/{challenge_id}")
        
        data_item["images_path"] = img_path
        data_item["locations"] = locations
        yield data_item

        # with open(full_data_path, 'w') as f:
        #     json.dump(full_data, f, indent=4, ensure_ascii=False)


def json_parser(text):
    # parse the json part inside the text
    # print(text)
    start = text.find("[")
    end = text.find("]") + 1
    clean_data = ' '.join(text[start:end].split()).replace("False", "false").replace("True", "true")
    print(clean_data)
    data = json.loads(clean_data)
    return data


@retry(tries=5, delay=10)
def split_transcript(transcript, game_nums, paraphrase=False):
    prompt = "Here is a youtube transcript of a player playing geoguessr, in which he is trying to guess the location based on the current views. He played " + f"{game_nums}" + " of games in total, each game has totally five rounds. The youtuber starts with prologue, " + f"{game_nums}" + " *5 rounds of games, and epilogue. Please split the scripts of the " + f"{game_nums}" + " *5 rounds of games, find useful clues in each round, and return me only a python list of the paraphrased clues (like xxx brands of cars, court style buildings, etc. Instead of using the player's point of view, state the clues in the scene in a neutral tone without mentioning the player) in each round in the transcripts with punctuation, and exclude the other parts. The clues should not showing the correctness of the final results. Also, the player sometimes get the answer correct, or get it wrong in the game. You should determine it based on his word. Your should only return a list of python dict without '\n', like [{'id': 'game1round1', 'transcript': clues in the first round, 'is_correct': True}, {...}] (Use double quotation marks instead, and make sure the keys are correct. The value of 'is_correct' should be true or false. The lenth of the list should be equal to " + f"{game_nums*5}" + " The transcript is as follows:\n"

    model = "gpt-4-1106-preview"
    
    def call_gpt():
        response = client.chat.completions.create(
            model=model,
            messages=[
                {'role': 'user', 'content': [{'type': 'text', 'text': prompt+transcript}]}
            ],
            max_tokens=4000
        )
        return response
    response = call_gpt()
    content = response.choices[0].message.content
    # print(content)
    content = json_parser(content)
    return content

def get_processed_data():
    data = load_data(full_data_path)
    for item in tqdm(data[:]):
        game_nums = len(item["challenge_url"])
        transcript = item["transcript"]
        locations = item["locations"]
        images_path = item["images_path"]
        # print("calling gpt to split transcript")
        # transcript_list = split_transcript(transcript, paraphrase=False)
        print("calling gpt to paraphrased transcript")
        paraphrased_transcript_list = split_transcript(transcript, game_nums=game_nums, paraphrase=True)
        # print(paraphrased_transcript_list)
        for i in range(game_nums):
            # there are data that misses images
            # if "image_not_available" in item:
            #     not_available_list = item["image_not_available"]
            # else:
            #     not_available_list = []
            for j in range(5):
                # if i+1 in not_available_list:
                #     continue
                yield {
                    "youtube_url": item["youtube_url"],
                    "challenge_url": item["challenge_url"][i],
                    # "transcript": transcript_list[i],
                    "paraphrased_transcript": paraphrased_transcript_list[i*5+j]["transcript"],
                    "is_correct": paraphrased_transcript_list[i*5+j]["is_correct"],
                    "location": locations[i][j],
                    "image_path": f"{images_path[i]}/{j+1}/combined.jpg"
                }

        

if __name__ == "__main__":
    dump_jsonl(get_data_of_videos(), full_data_path)
    # dump_jsonl(get_processed_data(), processed_data_path)

