# Geoguesser-Tryout-Project

This repository stores codes for the tryout project Geoguessr, which takes a list of links of youtube videos that play the game Geoguessr and its corresponding games, and outputs a json that points to locations, commentary (transcripts), and images.

## Repo structure

The project can be divided into several subtasks:

* Youtube Playlist [Play Along] --> Youtube Video and Geoguessr Game URLs (utils.play_list)
* Video URLs --> Video Transcrips (utils.youtube_transcript)
* Geoguessr URLs --> Locations (utils.location)
* Locations --> Images (utils.images)

## Data

The data are in the data file. 

* **urls.json**is the Youtube and Geoguessr urls of the [Play Along] playlist.
* **full_data.jsonl** is the raw retrieved data of images (path), transcripts, and locations.
* **processed_data.jsonl** is the processed data based on full_data.jsonl. The raw transcripts is paraphrased into **clues** in each games, and tagged with "true" or "false", depends on whether the player gets it right (therefore, the clues are divided into **positive and negative examples**). Images that can't be retrieved due to google map updates are dropped.

## Requirements

Run the following command to install the requirements:

    pip install requirements.txt

