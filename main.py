import json
import asyncio
from tqdm import tqdm
from utils.youtube_transcript import parse_video_id, get_script_from_youtube, merge_transcript, split_transcript
from utils.location import get_locations, parse_challenge_id
from utils.images import get_images, combine_images


data_path = "urls.json"
image_path = "images"
full_data_path = "full_data2.json"


def load_data():
    with open(data_path, 'r') as f:
        data = json.load(f)
    return data


def dump_jsonl(objects, file_name):
    out_file = open(file_name, "w")
    for obj in objects:
        tmp = out_file.write(json.dumps(obj, ensure_ascii=False) + "\n")
        out_file.flush()


def get_data_of_videos():
    data = load_data()
    
    full_data = []
    for videos in tqdm(data[14:]):
        youtube_url = videos["youtube_url"]
        challenge_url = videos["challenge_url"]
        data_item = {
            "youtube_url": youtube_url,
            "challenge_url": challenge_url
        }

        # get youtube transcript
        video_id = parse_video_id(youtube_url)
        transcript_list = get_script_from_youtube(video_id)
        data_item["transcript"] = merge_transcript(transcript_list)

        challenge_id = parse_challenge_id(challenge_url)

        # get locations
        data_item["locations"] = asyncio.run(get_locations(challenge_id))

        # get images
        for i, item in enumerate(data_item["locations"]):
            print(f"Getting images for round {i+1}")
            location = f"{item['lat']}, {item['lng']}"
            get_images(location, id=challenge_id, path=image_path, round=i+1)
            # if image does not exist, pass
            try:
                combine_images(image_path, challenge_id, round=i+1)
            except:
                data_item["image_not_available"] = [i+1]
        
        data_item["images_path"] = f"{image_path}/{challenge_id}"

        yield data_item

        # with open(full_data_path, 'w') as f:
        #     json.dump(full_data, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    dump_jsonl(get_data_of_videos(), full_data_path)








