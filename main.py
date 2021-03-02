import requests

import urllib3


def get_response(url, params=None):
    response = requests.get(url, params, verify=False)
    response.raise_for_status()
    return response


def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    url = 'https://api.hh.ru/vacancies'
    params = {'text': 'Python', 'area': '1', 'period': '30'}

    response = get_response(url, params)
    print(response.json())


if __name__ == '__main__':
    main()
