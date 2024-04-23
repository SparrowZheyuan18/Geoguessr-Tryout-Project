import google_streetview.api
from configuration import Config


def get_images(location, id):
    for heading in [0, 90, 180, 270]:
    # Define parameters for street view api
        params = [{
            'size': '640x640', # max 640x640 pixels
            'location': location,
            'heading': heading,
            'fov': 90,
            'key': Config.GCP_API_KEY
        }]

        # Create a results object
        results = google_streetview.api.results(params)
        print(results.links)

        # Download images to directory 'downloads'
        results.download_links(f'images/{id}/{heading}')


if __name__ == "__main__":
    location = '62.02823223925623, 129.70420196402097'
    get_images(location, "j5QTVixXslrbDXHj")