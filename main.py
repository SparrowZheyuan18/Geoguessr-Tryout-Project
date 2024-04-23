from youtube_transcript import parse_video_id, get_script_from_youtube, merge_transcript
from location import get_locations, parse_challenge_id
from images import get_images


youtube_url = "https://www.youtube.com/watch?v=t98r-YV6LnQ"
challenge_url = "https://www.geoguessr.com/challenge/j5QTVixXslrbDXHj"


def main():
    data_item = {
        "youtube_url": youtube_url,
        "challenge_url": challenge_url
    }

    # get youtube transcript
    video_id = parse_video_id(youtube_url)
    transcript_list = get_script_from_youtube(video_id)
    data_item["transcript"] = merge_transcript(transcript_list)
    # TODO: split transcript into 5 pieces

    challenge_id = parse_challenge_id(challenge_url)

    # get locations
    data_item["locations"] = get_locations(challenge_id)

    # get images
    for item in data_item["locations"]:
        location = f"{item['lat']}, {item['lng']}"
        get_images(location, challenge_id)






