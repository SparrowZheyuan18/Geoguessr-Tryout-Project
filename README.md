# Geoguesser-Tryout-Project

This repository stores codes for the tryout project Geoguessr, which takes a list of links of youtube videos that play the game Geoguessr and its corresponding games, and outputs a json that points to locations, commentary (transcripts), and images.

## Repo structure

The project can be divided into several subtasks:

- Youtube Playlist [Play Along] --> Youtube Video and Geoguessr Game URLs (utils.play_list)
- Video URLs --> Video Transcrips (utils.youtube_transcript)
- Geoguessr URLs --> Locations (utils.location)
- Locations --> Images (utils.images)

## Data

The data are in the data file. 

- **urls.json** is the Youtube and Geoguessr urls of the [Play Along] playlist.
- **full_data.jsonl** is the raw retrieved data of images (path), transcripts, and locations.
- **processed_data.jsonl** is the processed data based on full_data.jsonl. The raw transcripts is paraphrased into **clues** in each games, and tagged with "true" or "false", depends on whether the player gets it right (therefore, the clues are divided into **positive and negative examples**). Images that can't be retrieved due to google map updating are dropped ().

After processing, the details of data is demonstrated as follows:

| Category                    | Value   |
|-----------------------------|---------|
| Video Number                | 31      |
| Processed Data Number       | 152     |
| Commentary length per video | 3119.61 |
| Clue length per data        | 22.95   |
| Correct Clues               | 89      |
| Incorrect Clues             | 63      |

## Requirements

After cloning the repo and get into the dictionary, run the following command to install the requirements:

```bash
pip install -r requirements.txt
```

## Usage

First, set ncfa_cookie, Google Cloud Platform API-KEY, and OPENAI API-KEY in configration.py

- The ncfa cookie is for data from Geoguessr.com. To get one, login to geoguessr, open dev tools, go to Application/Storage/Cookies and copy the value of _ncfa.

- The GCP API-KEY is for images from google streetview.

- The OPENAI KEY is for getting clues from transcripts, which is not neccessary for simply getting the original data.

The Geoguessr [Play Along Youtube Playlist] is https://www.youtube.com/playlist?list=PL_japiE6QKWq-MCBz_wNr92yw0-HWeY2v.


### Getting the URLs 

```bash
python -m utils.play_list
```
The urls have been stored in /data/urls.json.

### Get data

```bash
python -m main
```

## Details

After processing, the data item in processed_data.jsonl are like follows:

```json
{
    "youtube_url": "https://youtube.com/watch?v=m0Od04q2idc&list=PL_japiE6QKWq-MCBz_wNr92yw0-HWeY2v&index=2", 
    "challenge_url": "https://www.geoguessr.com/challenge/NCkuJKocTTTcoyLJ", 
    "paraphrased_transcript": "Hebrew language signs, red poo sign possibly indicating a dog toilet, Bank Haifa possibly mistaking it for Maccabi Haifa, Jewish-themed shops, reference to Eilat indicating an Israeli location, looking eastward over the sea, and nearby Bank Apollon establishment", 
    "is_correct": true, 
    "location": {
        "round": 1, 
        "lat": 29.55659295332422, 
        "lng": 34.951060173415044
        }, 
    "image_path": "images/NCkuJKocTTTcoyLJ/1/combined.jpg"
}
```

- **paraphrased_transcipt**: the clues based on the original transcripts, extracted by GPT-4.
- **is_correct**: whether the clues successfully leads to the correct locations. True or false.
- **location**: the location of this round of Geoguessr game, represented by latitude and longtitude.
- **image_path**: the path to the image of this location. The path is composed of challenge id, round number. Note that when playing, Geoguessr shows a panorama view. Therefore, in order to contain all information needed in a image, I combined four pictures with 90 fov (field of view) and 90 heading, following [(Haas et al., 2024)](https://arxiv.org/pdf/2307.05845.pdf). The combined images now look like:

![Example of combined images](data/images/NCkuJKocTTTcoyLJ/1/combined.jpg)


## Experiments


## Automatic Playing Geoguessr Demo

Before I found how to request Geoguessr game information, I developed a script to automatically play Geoguessr game, by manipulating the website. This script can be use to drive Language Models to play this game directly. To try this out, simply run the following codes:

```python
python simulate_geoguessr.py
```

Note that this script can be really slow. 

## Possible Issues:

There are possible issues with this dataset. 

- **Updating of google map**: The google streetview api updates their service and streetview images from time to time. Some of the locations in Geoguessr games are no longer available, others might encounter a few mismatches between the image and the clues after it has been updated (e.g. A recognizable sign was removed).

- **Quality of clues**: The clues are now collected based of the transcripts from Youtube, with is quite noisy. Though I use GPT to paraphrase the clues, it can be too easy or too hard for models to do the task. (e.g. the clues state the location directly, or clues are not that helpful)

- **Our contributions:** [(Haas et al., 2024)](https://arxiv.org/pdf/2307.05845.pdf) builds models to do geoguessr tasks and achieved good results. Their dataset is similar to us, except for the CoT reasoning part. I'm considering ideas like [(Qi et al., 2024)](https://arxiv.org/pdf/2402.04236), which train Vision Language Models to dive into details of images, as our task is quite like manipulate the images to discover clues and do visual reasoning.