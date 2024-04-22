import asyncio
from geoguessr import Geoguessr


ncfa = "68tNhgbHV0y67QQxY%2BraTOE%2BMQfZTnLW0dtG3fPGZY4%3DqY0t%2BwIBRff1%2F9My5TLxODD3rE7fDNzloBHhHEHEV9CXT3uCAnZnAbJr8v3wz3daUyZ%2Fbg7RQSFbpl1G6HHKlJd1MxDbX6e8dDE6%2BTj%2FHmc%3D"


async def main(challenge_id):
    geoguessr = Geoguessr(ncfa)
    await geoguessr.play_challenge(challenge_id)
    # challenge_info = await geoguessr.get_challenge_game_info(challenge_id)
    locations = await geoguessr.get_challenge_locations(challenge_id)
    print(locations)
    await geoguessr.session.close()


if __name__ == "__main__":
    challenge_id = "j5QTVixXslrbDXHj"
    asyncio.run(main())
