import aiohttp


class Geoguessr:
    def __init__(self, ncfa):
        self.ncfa = ncfa
        self.base_url = "https://www.geoguessr.com/api/v3/"
        self.headers = {
            "Content-Type": "application/json",
            "cookie": f"_ncfa={self.ncfa}",
        }
        self.session = aiohttp.ClientSession(headers=self.headers)

    async def play_challenge(self, challenge_id):
        for i in range(5):
            async with self.session.post(
                f"{self.base_url}challenges/{challenge_id}",
                json={},
            ) as response:
                data = await response.json()
                game_id = data["token"]
            await self.play_game(game_id, i)
    
    async def play_game(self, game_id, round_id):
        request_data = {
            "token": game_id,
            "lat": 0,
            "lng": 0,
            "timedOut": True
        }
        await self.session.post(
            f"{self.base_url}games/{game_id}",
            json=request_data,
        )
        if round_id < 4:
            await self.session.get(
                f"{self.base_url}games/{game_id}?client=web"
            )

    async def get_challenge_game_info(self, challenge_id):
        async with self.session.get(
            f"{self.base_url}challenges/{challenge_id}/game",
        ) as response:
            data = await response.json()
            return data
        
    async def get_challenge_locations(self, challenge_id):
        async with self.session.get(
            f"{self.base_url}challenges/{challenge_id}/game",
        ) as response:
            data = await response.json()
            locations = []
            for i, round in enumerate(data["rounds"]):
                locations.append({
                    "round": i+1,
                    "lat": round["lat"],
                    "lng": round["lng"],
                })
            return locations