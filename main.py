import os
import requests
from terminaltables import AsciiTable
from dotenv import load_dotenv


def predict_salary(salary_from, salary_to):
    if salary_from and not salary_to:
        return int(salary_from * 1.2)
    if not salary_from and salary_to:
        return int(salary_to * 0.8)
    if salary_from and salary_to:
        return int((salary_from + salary_to) / 2)
    else:
        return None


def get_table(title, dic_language):
    table_data = [
        ['Язык программирования', 'Найдено вакансий',
         'Обработано вакансий', 'Средняя зарплата']
    ]

    for language in dic_language:
        row = [language,
               dic_language[language]['vacancies_found'],
               dic_language[language]['vacancies_processed'],
               dic_language[language]['average_salary']
               ]
        table_data.append(row)

    table = AsciiTable(table_data, title)
    return table.table


def get_vacancies_sj(keyword, sj_token):
    vacancies_found = 0
    vacancies_processed = 0
    vacancies_processed_sum = 0
    page = 0
    area_moscow = 4
    per_page = 10
    development_and_programming = 48
    objects = True
    salaries = []
    while objects:
        headers = {
            'X-Api-App-Id': sj_token
        }
        params = {
            "keyword": keyword,
            "t": area_moscow,
            "count": per_page,
            "catalogues": development_and_programming,
            "page": page,
        }
        response = requests.get("https://api.superjob.ru/2.0/vacancies/", headers = headers, params=params)
        response.raise_for_status()
        all_vacancies = response.json()
        for vacancy in all_vacancies["objects"]:
            vacancies_found += 1
            if not vacancy["currency"] == 'rub':
                continue
            salaries.append(predict_salary(vacancy["payment_from"],vacancy["payment_to"]))
        page += 1
        objects = all_vacancies["objects"]
    for salary in salaries:
        if salary:
            vacancies_processed += 1
            vacancies_processed_sum += salary
    try:
        average_salary = int(vacancies_processed_sum/vacancies_processed)
    except ZeroDivisionError:
        average_salary = 0

    return vacancies_found, vacancies_processed, average_salary


def get_statistics_sj(languages, sj_token):
    dic_language = {}

    for language in languages:
        vacancies_found, vacancies_processed, average_salary = (
            get_vacancies_sj(f'Программист {language}', sj_token))
        dic_statistics = {'vacancies_found': vacancies_found,
                          'vacancies_processed': vacancies_processed,
                          'average_salary': average_salary}
        dic_language.update({language: dic_statistics})

    return dic_language


def get_vacancies_hh(keyword):
    vacancies_found = 0
    vacancies_processed = 0
    vacancies_processed_sum = 0
    page = 0
    pages = 1
    period_days = 30
    area_moscow = 1
    per_page = 100
    list_salary = []

    while page < pages:

        params = {
            "text": keyword,
            "area": area_moscow,
            "per_page": per_page,
            "period": period_days,
            "page": page,
        }
        response = requests.get("https://api.hh.ru/vacancies", params=params)
        response.raise_for_status()
        all_vacancies = response.json()

        for vacancy in all_vacancies["items"]:
            salary = vacancy["salary"]
            if not salary:
                continue
            if not salary['currency'] == 'RUR':
                continue
            list_salary.append(predict_salary(salary['from'], salary['to']))

        vacancies_found = all_vacancies["found"]
        pages = all_vacancies["pages"]
        page += 1

    for salary in list_salary:
        if salary:
            vacancies_processed += 1
            vacancies_processed_sum += salary

    average_salary = int(vacancies_processed_sum/vacancies_processed)

    return vacancies_found, vacancies_processed, average_salary


def get_statistics_hh(languages):
    dic_language = {}

    for language in languages:
        vacancies_found, vacancies_processed, average_salary = get_vacancies_hh(f'Программист {language}')

        dic_statistics = {'vacancies_found': vacancies_found,
                          'vacancies_processed': vacancies_processed,
                          'average_salary': average_salary}
        dic_language.update({language: dic_statistics})

    return dic_language


def main():
    load_dotenv()
    sj_token = os.environ['SJ_TOKEN']
    title_sj = 'SuperJob Moscow'
    title_hh = 'HeadHunter Moscow'
    languages = ['python', 'java', 'javascript']
    print(get_table(title_sj, get_statistics_sj(languages, sj_token)))
    print(get_table(title_hh, get_statistics_hh(languages)))


if __name__ == '__main__':
    main()
