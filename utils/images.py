import google_streetview.api
from configuration import Config
from PIL import Image
from retry import retry


def get_images(location, id, path, round):
    for heading in [0, 90, 180, 270]:
    # Define parameters for street view api
        params = [{
            'size': '640x640', # max 640x640 pixels
            'location': location,
            'heading': heading,
            'fov': 90,
            'key': Config.GCP_API_KEY
        }]

        @retry(tries=5, delay=2)
        def streetview_api():
            return google_streetview.api.results(params)
        results = streetview_api()
        # print(results.links)
        results.download_links(f'{path}/{id}/{round}/{heading}')


def combine_images(path, challenge_id, round):
    image0 = Image.open(f'{path}/{challenge_id}/{round}/0/gsv_0.jpg')
    image90 = Image.open(f'{path}/{challenge_id}/{round}/90/gsv_0.jpg')
    image180 = Image.open(f'{path}/{challenge_id}/{round}/180/gsv_0.jpg')
    image270 = Image.open(f'{path}/{challenge_id}/{round}/270/gsv_0.jpg')

    width, height = image0.size
    total_width = width * 4

    new_image = Image.new('RGB', (total_width, height))
    new_image.paste(image0, (0, 0))
    new_image.paste(image90, (width, 0))
    new_image.paste(image180, (width*2, 0))
    new_image.paste(image270, (width*3, 0)) 

    new_image.save(f'{path}/{challenge_id}/{round}/combined.jpg')

    


if __name__ == "__main__":
    location = '62.02823223925623, 129.70420196402097'
    get_images(location, "j5QTVixXslrbDXHj", "images", round=1)
    combine_images("images", "j5QTVixXslrbDXHj", round=1)