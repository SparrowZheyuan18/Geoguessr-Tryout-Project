from youtube_transcript import parse_video_id, get_script_from_youtube, merge_transcript


youtube_url = "https://www.youtube.com/watch?v=t98r-YV6LnQ"
challenge_url = "https://www.geoguessr.com/challenge/j5QTVixXslrbDXHj"


def main():
    video_id = parse_video_id(youtube_url)
    transcript_list = get_script_from_youtube(video_id)
    transcript = merge_transcript(transcript_list)