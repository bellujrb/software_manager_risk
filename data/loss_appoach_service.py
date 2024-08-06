import requests

from config.settings import BASE_API_URL


def post_losshigh_specific(loss_type):
    url = f'{BASE_API_URL}api/losshigh-specific'
    headers = {'Content-Type': 'application/json', 'Loss': loss_type}
    response = requests.post(url, headers=headers)
    return response
