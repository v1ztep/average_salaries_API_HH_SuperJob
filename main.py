import requests

import urllib3


def get_response(url, params=None):
    response = requests.get(url, params, verify=False)
    response.raise_for_status()
    return response


def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    languages = ('JavaScript', 'Java', 'Python', 'Ruby', 'PHP', 'C++', 'C#',
                 'C', 'Go', 'Shell', 'Objective-C', 'Scala', 'Swift',
                 'TypeScript')
    url = 'https://api.hh.ru/vacancies'

    vacancies_count = {}
    for lang in languages:
        params = {'text': f'Программист {lang}', 'area': '1', 'period': '30'}
        response = get_response(url, params)
        found_num = response.json()['found']
        vacancies_count[lang] = found_num

    print(vacancies_count)

if __name__ == '__main__':
    main()
