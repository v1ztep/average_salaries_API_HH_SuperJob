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


def predict_rub_salary(salary_from, salary_to):
    if salary_from and salary_to:
        average_salary = (salary_from + salary_to) / 2
        return average_salary
    elif salary_from:
        return salary_from * 1.2
    else:
        return salary_to * 0.8


def get_hh_stats(professions):
    hh_api_url = 'https://api.hh.ru/vacancies'
    desired_currency = 'RUR'
    vacancies_stats = {}
    for profession in professions:
        first_page = 0
        vacancies_salary = []
        vacancies_found = []
        for page in count(first_page):
            params = {'text': profession, 'area': '1', 'period': '30',
                      'per_page': 100, 'page': page}
            response = get_response(hh_api_url, params)
            vacancies_details = response.json()

            vacancies = vacancies_details['items']
            for vacancy in vacancies:
                salary = vacancy['salary']
                if not salary:
                    continue
                currency = vacancy['salary']['currency']
                if currency != desired_currency:
                    continue

                salary_from = salary['from']
                salary_to = salary['to']
                calculated_salary = predict_rub_salary(salary_from, salary_to)
                vacancies_salary.append(calculated_salary)

            if page == first_page:
                vacancies_found = vacancies_details['found']

            last_page = vacancies_details['pages'] - 1
            if page >= last_page:
                print(f'{profession} Ok')
                break

        average_salary = statistics.mean(vacancies_salary)
        lang = profession.split()[-1]
        vacancies_stats[lang] = {
            'vacancies_found': vacancies_found,
            'vacancies_processed': len(vacancies_salary),
            'average_salary': int(average_salary),
        }
    return vacancies_stats


def main():
    load_dotenv()
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    professions = (
        'Программист JavaScript', 'Программист Java', 'Программист Python',
        'Программист Ruby', 'Программист PHP', 'Программист C++',
        'Программист C#', 'Программист C', 'Программист Go',
        'Программист Shell', 'Программист Objective-C', 'Программист Scala',
        'Программист Swift', 'Программист TypeScript')
    superjob_api_key = os.getenv('SUPERJOB_API_KEY')

    # hh_vacancies_stats = get_hh_stats(professions)
    # print(hh_vacancies_stats)

    sj_api_url = 'https://api.superjob.ru/2.0/vacancies/'
    headers = {
        'X-Api-App-Id': superjob_api_key,
    }
    params = {'town': 4, 'keyword': 'Программист Python', }
    response = get_response(sj_api_url, params=params, headers=headers)

    with open("description.json", "w", encoding='utf8') as file:
        json.dump(response.json(), file, ensure_ascii=False, indent=4)

    superjob_vacancies = response.json()['objects']
    for vacancy in superjob_vacancies:
        vacancy_profession = vacancy['profession']
        vacancy_town = vacancy['town']['title']
        print(f'{vacancy_profession}, {vacancy_town}')

if __name__ == '__main__':
    main()
