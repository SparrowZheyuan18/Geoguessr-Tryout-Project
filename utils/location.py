import asyncio
from utils.geoguessr import Geoguessr
from configuration import Config


ncfa = Config.NCFA

def parse_challenge_id(challenge_url):
    return challenge_url.split("/")[-1]


async def get_locations(challenge_id):
    geoguessr = Geoguessr(ncfa)
    await geoguessr.play_challenge(challenge_id)
    # challenge_info = await geoguessr.get_challenge_game_info(challenge_id)
    locations = await geoguessr.get_challenge_locations(challenge_id)
    # print("locations:", locations)
    await geoguessr.session.close()
    return locations



if __name__ == "__main__":
    challenge_url = "https://www.geoguessr.com/challenge/j5QTVixXslrbDXHj"
    challenge_id = parse_challenge_id(challenge_url)
    asyncio.run(get_locations(challenge_id))
