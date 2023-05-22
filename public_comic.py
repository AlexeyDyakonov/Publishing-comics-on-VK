import os
import random

import requests
from dotenv import load_dotenv

VK_API_VERSION = 5.131


def save_random_comic_from_xkcd(comics_filename, url):
    comics_response = requests.get(url)
    comics_response.raise_for_status()
    comics = comics_response.json()
    img_url = comics['img']
    comics_comment = comics['alt']
    title = comics['title']
    comics_image_response = requests.get(img_url)
    comics_image_response.raise_for_status()

    with open(comics_filename, 'wb') as file:
        file.write(comics_image_response.content)

    return comics_comment, title


def get_comic_data_from_server(access_token, vk_group_id):
    url_server = 'https://api.vk.com/method/photos.getWallUploadServer'
    params_server = {
            'access_token': access_token,
            'v': VK_API_VERSION,
            'group_id': vk_group_id
        }

    response = requests.get(url_server, params=params_server)
    response.raise_for_status()
    upload_url = response.json()['response']['upload_url']
    with open('comics.png', 'rb') as file:
        files = {
            'photo': file
        }
        response = requests.post(upload_url, files=files)
        response.raise_for_status()
        information_to_load_picture = response.json()
        server = information_to_load_picture['server']
        photo = information_to_load_picture['photo']
        hash = information_to_load_picture['hash']
    return server, hash, photo


def save_comic(access_token, vk_group_id):
    save_photo_url = 'https://api.vk.com/method/photos.saveWallPhoto'
    server, hash, photo = get_comic_data_from_server(access_token, vk_group_id)
    params_save = {
            'access_token': access_token,
            'v': VK_API_VERSION,
            'group_id': vk_group_id,
            'photo': photo,
            "server": server,
            'hash': hash
        }
    response_save = requests.post(save_photo_url, params=params_save)
    response_save.raise_for_status()
    owner_id = response_save.json()['response'][0]['owner_id']
    media_id = response_save.json()['response'][0]['id']
    return owner_id, media_id


def post_coimic_in_group(access_token, vk_group_id, filename, url_comic):
    owner_id, media_id = save_comic(access_token, vk_group_id)
    comics_comment, title = save_random_comic_from_xkcd(filename, url_comic)
    post_url = 'https://api.vk.com/method/wall.post'

    params_post = {
            'access_token': access_token,
            'v': VK_API_VERSION,
            'group_id': vk_group_id,
            'owner_id': -vk_group_id,
            'from_group': 0,
            'attachments': f'photo{owner_id}_{media_id}',
            'message': f'{title} \n {comics_comment}'
        }
    response_post = requests.post(post_url, params=params_post)
    return response_post


if __name__ == '__main__':

    load_dotenv()
    access_token = os.environ['ACCESS_TOKEN']
    vk_group_id = int(os.environ['VK_GROUP_ID'])
    filename = 'comics.png'

    number_of_first_comic = 1
    number_of_last_comic = 2778
    comic_number = random.randint(number_of_first_comic,
                                  number_of_last_comic)

    url_comic = f"https://xkcd.com/{comic_number}/info.0.json"

    save_random_comic_from_xkcd(filename, url_comic)

    post_coimic_in_group(access_token, vk_group_id, filename, url_comic)

    os.remove('comics.png')
