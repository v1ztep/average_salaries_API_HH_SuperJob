import json
import os
import statistics
from itertools import count

import requests
import urllib3
from dotenv import load_dotenv


def get_response(url, params=None, headers=None):
    response = requests.get(url, params=params, headers=headers, verify=False)
    response.raise_for_status()
    return response


def predict_rub_salary(vacancy):
    salary = vacancy['salary']
    if salary is None:
        return None

    desired_currency = 'RUR'
    currency = vacancy['salary']['currency']
    if currency != desired_currency:
        return None

    salary_from = salary['from']
    salary_to = salary['to']
    if salary_from and salary_to:
        average_salary = (salary_from + salary_to) / 2
        return average_salary
    elif salary_from:
        return salary_from * 1.2
    else:
        return salary_to * 0.8


def get_hh_stats(languages):
    hh_api_url = 'https://api.hh.ru/vacancies'
    vacancies_stats = {}
    for lang in languages:
        first_page = 0
        vacancies_salary = []
        vacancies_found = []
        for page in count(first_page):
            params = {'text': f'Программист {lang}', 'area': '1',
                      'period': '30', 'per_page': 100, 'page': page}
            response = get_response(hh_api_url, params)
            vacancies_details = response.json()

            vacancies = vacancies_details['items']
            for vacancy in vacancies:
                salary = predict_rub_salary(vacancy)
                if salary:
                    vacancies_salary.append(salary)

            if page == first_page:
                vacancies_found = vacancies_details['found']

            last_page = vacancies_details['pages'] - 1
            if page >= last_page:
                print(f'{lang} Ok')
                break

        average_salary = statistics.mean(vacancies_salary)
        vacancies_stats[lang] = {
            'vacancies_found': vacancies_found,
            'vacancies_processed': len(vacancies_salary),
            'average_salary': int(average_salary),
        }
    return vacancies_stats


def main():
    load_dotenv()
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    languages = ('JavaScript', 'Java', 'Python', 'Ruby', 'PHP', 'C++', 'C#',
                 'C', 'Go', 'Shell', 'Objective-C', 'Scala', 'Swift',
                 'TypeScript')
    superjob_api_key = os.getenv('SUPERJOB_API_KEY')

    # hh_vacancies_stats = get_hh_stats(languages)
    # print(hh_vacancies_stats)

    superjob_api_url = 'https://api.superjob.ru/2.0/vacancies/'
    headers = {
        'X-Api-App-Id': superjob_api_key,
    }
    params = {'town': 4, 'keyword': 'Программист Python'}
    response = get_response(superjob_api_url, params=params, headers=headers)

    with open("description.json", "w", encoding='utf8') as file:
        json.dump(response.json(), file, ensure_ascii=False, indent=4)

    superjob_vacancies = response.json()['objects']
    for vacancy in superjob_vacancies:
        vacancy_profession = vacancy['profession']
        vacancy_town = vacancy['town']['title']
        print(f'{vacancy_profession}, {vacancy_town}')

if __name__ == '__main__':
    main()
