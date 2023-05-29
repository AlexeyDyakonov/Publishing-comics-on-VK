import os
import random

import requests
from dotenv import load_dotenv

VK_API_VERSION = 5.131


def check_vk_errors(feedback):
    if 'error' in feedback:
        raise requests.HTTPError(feedback['error'])


def save_random_comic_from_xkcd(
        comics_filename,
        comics_number):
    url = f"https://xkcd.com/{comics_number}/info.0.json"
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


def uploads_comics_to_vk_server(
        access_token,
        vk_group_id,
        filename):
    server_url = 'https://api.vk.com/method/photos.getWallUploadServer'
    server_params = {
            'access_token': access_token,
            'v': VK_API_VERSION,
            'group_id': vk_group_id
        }

    response = requests.get(server_url, params=server_params)
    response.raise_for_status()
    picture_url = response.json()
    check_vk_errors(picture_url)
    upload_url = picture_url['response']['upload_url']
    with open(filename, 'rb') as file:
        files = {
            'photo': file
        }
        response = requests.post(upload_url, files=files)
    response.raise_for_status()
    load_picture = response.json()
    vk_server = load_picture['server']
    vk_photo = load_picture['photo']
    vk_hash = load_picture['hash']
    return vk_server, vk_hash, vk_photo


def save_comic_in_album_vk(
        access_token,
        vk_group_id,
        vk_server,
        vk_hash,
        vk_photo):
    save_photo_url = 'https://api.vk.com/method/photos.saveWallPhoto'
    params_save = {
            'access_token': access_token,
            'v': VK_API_VERSION,
            'group_id': vk_group_id,
            'photo': vk_photo,
            "server": vk_server,
            'hash': vk_hash
        }
    save_response = requests.post(save_photo_url, params=params_save)
    save_response.raise_for_status()
    information_to_get_save_url = save_response.json()
    check_vk_errors(information_to_get_save_url)
    owner_id = information_to_get_save_url['response'][0]['owner_id']
    media_id = information_to_get_save_url['response'][0]['id']
    return owner_id, media_id


def post_comic_in_group(
        access_token,
        vk_group_id,
        comics_comment,
        title,
        owner_id,
        media_id):
    post_url = 'https://api.vk.com/method/wall.post'
    post_params = {
            'access_token': access_token,
            'v': VK_API_VERSION,
            'group_id': vk_group_id,
            'owner_id': -vk_group_id,
            'from_group': 0,
            'attachments': f'photo{owner_id}_{media_id}',
            'message': f'{title} \n {comics_comment}'
        }
    post_response = requests.post(post_url, params=post_params)
    post_response.raise_for_status()
    information_to_get_post_url = post_response.json()
    check_vk_errors(information_to_get_post_url)
    return post_response


def main():
    try:
        load_dotenv()
        vk_access_token = os.environ['VK_ACCESS_TOKEN']
        vk_group_id = int(os.environ['VK_GROUP_ID'])
        comics_filename = 'comics.png'

        number_of_first_comic = 1
        number_of_last_comic = 2778
        comics_number = random.randint(
            number_of_first_comic,
            number_of_last_comic
        )
        comics_comment, title = save_random_comic_from_xkcd(
            comics_filename,
            comics_number
        )
        vk_server, vk_hash, vk_photo = uploads_comics_to_vk_server(
            vk_access_token,
            vk_group_id,
            comics_filename
        )
        owner_id, media_id = save_comic_in_album_vk(
            vk_access_token,
            vk_group_id,
            vk_server,
            vk_hash,
            vk_photo
        )
        post_comic_in_group(
            vk_access_token,
            vk_group_id,
            comics_comment,
            title,
            owner_id,
            media_id
        )
    finally:
        os.remove('comics.png')


if __name__ == '__main__':
    main()

