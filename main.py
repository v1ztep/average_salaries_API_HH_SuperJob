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


def get_hh_stats(languages):
    hh_api_url = 'https://api.hh.ru/vacancies'
    desired_currency = 'RUR'
    vacancies_stats = {}
    for lang in languages:
        first_page = 0
        vacancies_salary = []
        vacancies_found = []
        for page in count(first_page):
            params = {'text': f'Программист {lang}', 'area': '1',
                      'period': '30', 'per_page': 100, 'page': page}
            response = get_response(hh_api_url, params=params)
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
                print(f'{lang} Ok')
                break

        average_salary = statistics.mean(vacancies_salary)
        vacancies_stats[lang] = {
            'vacancies_found': vacancies_found,
            'vacancies_processed': len(vacancies_salary),
            'average_salary': int(average_salary),
        }
    return vacancies_stats


def get_sj_stats(languages, superjob_api_key):
    sj_api_url = 'https://api.superjob.ru/2.0/vacancies/'
    desired_currency = 'rub'
    vacancies_stats = {}
    for lang in languages:
        first_page = 0
        vacancies_salary = []
        vacancies_found = []
        for page in count(first_page):
            params = {
                'town': 4, 'page': page, 'count': 10,
                'keywords[1][srws]': 1, 'keywords[1][keys]': lang
            }
            headers = {'X-Api-App-Id': superjob_api_key}
            response = get_response(sj_api_url, params=params, headers=headers)
            vacancies_details = response.json()

            if page == first_page:
                vacancies_found = vacancies_details['total']

            vacancies = vacancies_details['objects']
            if not vacancies:
                break

            for vacancy in vacancies:
                currency = vacancy['currency']
                if currency != desired_currency:
                    continue

                salary_from = vacancy['payment_from']
                salary_to = vacancy['payment_to']
                if not salary_from and not salary_to:
                    continue

                calculated_salary = predict_rub_salary(salary_from, salary_to)
                vacancies_salary.append(calculated_salary)

            next_page = vacancies_details['more']
            if not next_page:
                print(f'{lang} Ok')
                break

        if vacancies_salary:
            average_salary = statistics.mean(vacancies_salary)
        else:
            average_salary = 0
        vacancies_stats[lang] = {
            'vacancies_found': vacancies_found,
            'vacancies_processed': len(vacancies_salary),
            'average_salary': int(average_salary),
        }
    return vacancies_stats


def main():
    load_dotenv()
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    languages = (
        'JavaScript', 'Java', 'Python', 'Ruby', 'PHP', 'C++', 'C#', 'C', 'Go',
        'Shell', 'Objective-C', 'Scala', 'Swift', 'TypeScript')
    superjob_api_key = os.getenv('SUPERJOB_API_KEY')

    # hh_vacancies_stats = get_hh_stats(languages)
    # print(hh_vacancies_stats)

    sj_vacancies_stats = get_sj_stats(languages, superjob_api_key)
    print(sj_vacancies_stats)

    with open("description.json", "w", encoding='utf8') as file:
        json.dump(sj_vacancies_stats, file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()
