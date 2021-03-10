import os
import statistics
from itertools import count

import requests
import urllib3
from dotenv import load_dotenv
from terminaltables import SingleTable


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


def get_vacancies_salaries_hh(vacancies):
    desired_currency = 'RUR'
    vacancies_salaries = []
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
        vacancies_salaries.append(calculated_salary)
    return vacancies_salaries


def get_hh_vacancies_stats(lang):
    hh_api_url = 'https://api.hh.ru/vacancies'
    first_page = 0
    moscow_area = 1
    period_days = 30
    vacansies_per_page = 100

    params = {
        'text': f'Программист {lang}',
        'area': moscow_area,
        'period': period_days,
        'per_page': vacansies_per_page,
        'page': None
    }

    vacancies_salaries = []
    for page in count(first_page):
        params['page'] = page
        response = get_response(hh_api_url, params=params)
        vacancies_details = response.json()

        vacancies = vacancies_details['items']
        vacancies_salaries.extend(get_vacancies_salaries_hh(vacancies))

        last_page = vacancies_details['pages'] - 1
        if page >= last_page:
            break

    vacancies_found = vacancies_details['found']
    vacancies_processed = len(vacancies_salaries)
    average_salary = statistics.mean(vacancies_salaries)

    return vacancies_found, vacancies_processed, average_salary


def predict_rub_salary_hh(languages):
    vacancies_stats = {}
    for lang in languages:
        vacancies_found, vacancies_processed, average_salary = \
            get_hh_vacancies_stats(lang)

        vacancies_stats[lang] = {
            'vacancies_found': vacancies_found,
            'vacancies_processed': vacancies_processed,
            'average_salary': int(average_salary),
        }
    return vacancies_stats


def get_vacancies_salaries_sj(vacancies):
    desired_currency = 'rub'

    vacancies_salaries = []
    for vacancy in vacancies:
        currency = vacancy['currency']
        if currency != desired_currency:
            continue

        salary_from = vacancy['payment_from']
        salary_to = vacancy['payment_to']
        if not salary_from and not salary_to:
            continue

        calculated_salary = predict_rub_salary(salary_from, salary_to)
        vacancies_salaries.append(calculated_salary)

    return vacancies_salaries


def get_sj_vacancies_stats(lang, superjob_api_key):
    sj_api_url = 'https://api.superjob.ru/2.0/vacancies/'
    first_page = 0
    moscow_town = 4
    vacansies_per_page = 10
    search_on_position = 1

    params = {
        'town': moscow_town,
        'page': None,
        'count': vacansies_per_page,
        'keywords[1][srws]': search_on_position,
        'keywords[1][keys]': lang
    }
    headers = {'X-Api-App-Id': superjob_api_key}

    vacancies_salaries = []
    for page in count(first_page):
        params['page'] = page
        response = get_response(sj_api_url, params=params, headers=headers)
        vacancies_details = response.json()

        vacancies = vacancies_details['objects']
        if not vacancies:
            break

        vacancies_salaries.extend(get_vacancies_salaries_sj(vacancies))

        more_page = vacancies_details['more']
        if not more_page:
            break

    vacancies_found = vacancies_details['total']
    vacancies_processed = len(vacancies_salaries)
    if vacancies_salaries:
        average_salary = statistics.mean(vacancies_salaries)
    else:
        average_salary = 0

    return vacancies_found, vacancies_processed, average_salary


def predict_rub_salary_sj(languages, superjob_api_key):
    vacancies_stats = {}
    for lang in languages:
        vacancies_found, vacancies_processed, average_salary = \
            get_sj_vacancies_stats(lang, superjob_api_key)

        vacancies_stats[lang] = {
            'vacancies_found': vacancies_found,
            'vacancies_processed': vacancies_processed,
            'average_salary': int(average_salary),
        }

    return vacancies_stats


def get_table_stats(vacancies_stats, title):
    stats_table = [(
        'Язык программирования',
        'Вакансий найдено',
        'Вакансий обработано',
        'Средняя зарплата'
    )]

    for lang, stats in vacancies_stats.items():
        lang_stats = [
            lang,
            stats['vacancies_found'],
            stats['vacancies_processed'],
            stats['average_salary']
        ]
        stats_table.append(lang_stats)

    table_instance = SingleTable(stats_table, title)
    return table_instance.table


def main():
    load_dotenv()
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    languages = (
        'JavaScript',
        'Java',
        'Python',
        'Ruby',
        'PHP',
        'C++',
        'C#',
        'C',
        'Go',
        'Shell',
        'Objective-C',
        'Scala',
        'Swift',
        'TypeScript',
        '1C'
    )
    superjob_api_key = os.getenv('SUPERJOB_API_KEY')

    hh_vacancies_stats = predict_rub_salary_hh(languages)
    hh_table_stats = get_table_stats(hh_vacancies_stats, 'HeadHunter Moscow')
    print(hh_table_stats)

    sj_vacancies_stats = predict_rub_salary_sj(languages, superjob_api_key)
    sj_table_stats = get_table_stats(sj_vacancies_stats, 'SuperJob Moscow')
    print(sj_table_stats)


if __name__ == '__main__':
    main()
