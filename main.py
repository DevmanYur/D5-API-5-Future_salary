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


def get_statistics_vacancies_hh(keyword):
    vacancies_found = 0
    vacancies_processed = 0
    vacancies_processed_sum = 0
    page = 0
    pages = 1
    list_salary = []
    while page < pages:
        params = {
            "text": keyword,
            "area": 1,
            "per_page": 100,
            "period": 30,
            "page": page,
        }
        response = requests.get("https://api.hh.ru/vacancies", params=params)
        response.raise_for_status()
        all_vacancies = response.json()
        for vacancy in all_vacancies["items"]:
            list_salary.append(predict_rub_salary_hh(vacancy))
        vacancies_found = all_vacancies["found"]
        pages = all_vacancies["pages"]
        page += 1

    for salary in list_salary:
        if salary:
            vacancies_processed += 1
            vacancies_processed_sum += salary
    average_salary = int(vacancies_processed_sum/vacancies_processed)

    return vacancies_found, vacancies_processed, average_salary


def predict_rub_salary_hh(vacancy):
    salary = vacancy["salary"]
    if salary:
        if salary['currency'] == 'RUR':
            return predict_salary(salary['from'], salary['to'])
    else:
        return None


def get_table_hh(languages):
    table_data = [['Язык программирования', 'Найдено вакансий',
                   'Обработано вакансий', 'Средняя зарплата']]
    title = 'HeadHunter Moscow'
    for language in languages:
        vacancies_found, vacancies_processed, average_salary = (
            get_statistics_vacancies_hh(f'Программист {language}'))
        row = [language, vacancies_found, vacancies_processed, average_salary]
        table_data.append(row)
    table = AsciiTable(table_data, title)
    return table.table


def get_statistics_vacancies_sj(keyword, sj_token):
    vacancies_found = 0
    vacancies_processed = 0
    vacancies_processed_sum = 0
    page = 0
    list_salary = []
    headers = {
        'X-Api-App-Id' : f'{sj_token}'
    }
    while page < 5:
        params = (
            ('count', '100'),
            ('page', page),
            ('catalogues', 48),
            ('t', '4'),
            ('keyword', keyword),
        )
        response = requests.get('https://api.superjob.ru/2.0/vacancies/',
                                headers=headers, params=params)
        response.raise_for_status()
        vacancies = response.json()
        for vacancy in vacancies["objects"]:
            vacancies_found += 1
            list_salary.append(predict_rub_salary_sj(vacancy))
        page += 1
    for salary in list_salary:
        if salary:
            vacancies_processed += 1
            vacancies_processed_sum += salary
    average_salary = int(vacancies_processed_sum/vacancies_processed)
    return vacancies_found, vacancies_processed, average_salary


def predict_rub_salary_sj(vacancy):
    if vacancy["currency"] == 'rub':
        if vacancy["payment_from"] > 0 and vacancy["payment_to"] > 0:
            return predict_salary(vacancy["payment_from"], vacancy["payment_to"])
        if vacancy["payment_from"] > 0 and vacancy["payment_to"] == 0:
            return predict_salary(vacancy["payment_from"], None)
        if vacancy["payment_from"] == 0 and vacancy["payment_to"] > 0:
            return predict_salary(None, vacancy["payment_to"])
    else:
        return None


def get_table_superjob(languages, sj_token):
    table_data = [
        ['Язык программирования', 'Найдено вакансий',
         'Обработано вакансий', 'Средняя зарплата']
    ]

    title = 'SuperJob Moscow'

    for language in languages:
        vacancies_found, vacancies_processed, average_salary = (
            get_statistics_vacancies_sj(f'Программист {language}', sj_token))
        row = [language, vacancies_found, vacancies_processed, average_salary]
        table_data.append(row)

    table = AsciiTable(table_data, title)
    return table.table


def main():
    load_dotenv()
    sj_token = os.environ['SJ_TOKEN']
    languages = ['python', 'java', 'javascript']
    print(get_table_hh(languages))
    print(get_table_superjob(languages, sj_token))


if __name__ == '__main__':
    main()
