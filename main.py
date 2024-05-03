import os
import requests
from terminaltables import AsciiTable
from dotenv import load_dotenv


def get_vacancies_processed_average_salary(salaries):
    vacancies_processed = 0
    vacancies_processed_sum = 0
    for salary in salaries:
        if salary:
            vacancies_processed += 1
            vacancies_processed_sum += salary
    try:
        average_salary = int(vacancies_processed_sum / vacancies_processed)
    except ZeroDivisionError:
        average_salary = 0
    return vacancies_processed, average_salary


def predict_salary(salary_from, salary_to):
    if salary_from and not salary_to:
        return int(salary_from * 1.2)
    if not salary_from and salary_to:
        return int(salary_to * 0.8)
    if salary_from and salary_to:
        return int((salary_from + salary_to) / 2)
    else:
        return None


def get_table(title, statistics):
    table_data = [
        ['Язык программирования', 'Найдено вакансий',
         'Обработано вакансий', 'Средняя зарплата']
    ]
    for language, statistic in statistics.items():
        row = [language,
               statistic['vacancies_found'],
               statistic['vacancies_processed'],
               statistic['average_salary']
               ]
        table_data.append(row)
    table = AsciiTable(table_data, title)
    return table.table


def get_vacancies_sj(keyword, sj_token):
    vacancies_found = 0
    page = 0
    area_moscow = 4
    per_page = 10
    development_and_programming = 48
    availability_page = True
    salaries = []
    while availability_page:
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
        response = requests.get("https://api.superjob.ru/2.0/vacancies/", headers=headers, params=params)
        response.raise_for_status()
        all_vacancies = response.json()
        for vacancy in all_vacancies["objects"]:
            if not vacancy["currency"] == 'rub':
                continue
            salaries.append(predict_salary(vacancy["payment_from"], vacancy["payment_to"]))
        vacancies_found = all_vacancies["total"]
        page += 1
        availability_page = all_vacancies["objects"]
    vacancies_processed, average_salary = get_vacancies_processed_average_salary(salaries)
    return vacancies_found, vacancies_processed, average_salary


def get_statistics_sj(languages, sj_token):
    statistics = {}

    for language in languages:
        vacancies_found, vacancies_processed, average_salary = (
            get_vacancies_sj(f'Программист {language}', sj_token))
        language_statistics = {'vacancies_found': vacancies_found,
                               'vacancies_processed': vacancies_processed,
                               'average_salary': average_salary}
        statistics.update({language: language_statistics})
    return statistics


def get_vacancies_hh(keyword):
    vacancies_found = 0
    page = 0
    pages = 1
    period_days = 30
    area_moscow = 1
    per_page = 100
    salaries = []

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
            salaries.append(predict_salary(salary['from'], salary['to']))

        vacancies_found = all_vacancies["found"]
        pages = all_vacancies["pages"]
        page += 1
    vacancies_processed, average_salary = get_vacancies_processed_average_salary(salaries)
    return vacancies_found, vacancies_processed, average_salary


def get_statistics_hh(languages):
    statistics = {}
    for language in languages:
        vacancies_found, vacancies_processed, average_salary = get_vacancies_hh(f'Программист {language}')

        language_statistics = {'vacancies_found': vacancies_found,
                               'vacancies_processed': vacancies_processed,
                               'average_salary': average_salary}
        statistics[language] = language_statistics
    return statistics


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
