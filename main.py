import requests

import urllib3


def get_response(url, params=None):
    response = requests.get(url, params, verify=False)
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
    elif salary_to:
        return salary_to * 0.8


def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    languages = ('JavaScript', 'Java', 'Python', 'Ruby', 'PHP', 'C++', 'C#',
                 'C', 'Go', 'Shell', 'Objective-C', 'Scala', 'Swift',
                 'TypeScript')
    url = 'https://api.hh.ru/vacancies'

    # vacancies_count = {}
    # for lang in languages:
    #     params = {'text': f'Программист {lang}', 'area': '1', 'period': '30'}
    #     response = get_response(url, params)
    #     found_num = response.json()['found']
    #     vacancies_count[lang] = found_num
    # print(vacancies_count)

    lang = 'Python'
    params = {'text': f'Программист {lang}', 'area': 1, 'period': 30}
    response = get_response(url, params)
    vacancies = response.json()['items']

    for vacancy in vacancies:
        salary = predict_rub_salary(vacancy)
        print(salary)


if __name__ == '__main__':
    main()
