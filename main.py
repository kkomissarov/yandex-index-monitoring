import json
import os
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup
from pandas import DataFrame

import config
from url_patterns import HOST_STAT_URL_TEMPLATE, INSEARCH_URL_TEMPLATE, USERID_URL


def get_auth_headers() -> dict:
    return {'Authorization': f'OAuth {config.TOKEN}'}


def get_sites() -> dict:
    return pd.read_excel(config.SITES_LIST_PATH).to_dict('records')


def get_user_id() -> str:
    r = requests.get(USERID_URL, headers=get_auth_headers())
    user_id = json.loads(r.text)['user_id']
    return user_id


def get_indexed_pages(user_id: str, host: str) -> set:
    host_stat_url = HOST_STAT_URL_TEMPLATE.format(user_id, host)
    insearch_url = INSEARCH_URL_TEMPLATE.format(user_id, host)

    r = requests.get(host_stat_url, headers=get_auth_headers())
    indexed_pages_quantity = json.loads(r.text)['searchable_pages_count']

    indexed_pages = set()
    params = {'offset': 0, 'limit': config.YANDEX_PER_REQUEST_PAGE_LIMIT}
    while params['offset'] < indexed_pages_quantity:
        r = requests.get(insearch_url, headers=get_auth_headers(), params=params)
        current_urls = {element['url'] for element in json.loads(r.text)['samples']}
        indexed_pages = indexed_pages.union(current_urls)
        params['offset'] += config.YANDEX_PER_REQUEST_PAGE_LIMIT

    return indexed_pages


def parse_sitemap(sitemap: str) -> set:
    r = requests.get(sitemap)
    soup = BeautifulSoup(r.text, 'xml')
    return {url.text for url in soup.find_all('loc')}


def export_data_to_excel(data: DataFrame, path: str, filename: str) -> None:
    os.makedirs(path, exist_ok=True)
    project_report = pd.ExcelWriter(os.path.join(path, filename), engine='xlsxwriter')
    data.to_excel(
        project_report,
        sheet_name='main_index_match',
        index=False,
        startcol=0
    )
    project_report.save()


def get_visual_report_data(indexed_pages: set, pages_in_sitemap: set) -> DataFrame:
    pages_in_index_but_not_in_sitemap = indexed_pages - pages_in_sitemap
    pages_is_sitemap_but_not_in_index = pages_in_sitemap - indexed_pages

    pages_in_index_but_not_in_sitemap_df = pd.DataFrame(
        pages_in_index_but_not_in_sitemap,
        columns=['pages_in_index_but_not_in_sitemap']
    )
    pages_is_sitemap_but_not_in_index_df = pd.DataFrame(
        pages_is_sitemap_but_not_in_index,
        columns=['pages_is_sitemap_but_not_in_index']
    )
    data = pd.concat([pages_in_index_but_not_in_sitemap_df, pages_is_sitemap_but_not_in_index_df], axis=1)
    return data


def get_recrawl_base_data(indexed_pages: set, pages_in_sitemap: set) -> DataFrame:
    pages_in_index_but_not_in_sitemap = indexed_pages - pages_in_sitemap
    pages_is_sitemap_but_not_in_index = pages_in_sitemap - indexed_pages
    all_pages_to_recrawl = list(pages_in_index_but_not_in_sitemap.union(pages_is_sitemap_but_not_in_index))
    data = pd.DataFrame(all_pages_to_recrawl, columns=['urls'])
    return data


def make_visual_report(project_name: str, path: str, indexed_pages: set, pages_in_sitemap: set) -> None:
    data = get_visual_report_data(indexed_pages, pages_in_sitemap)
    filename = config.VISUAL_REPORT_FILENAME_TEMPLATE.format(
        project_name=project_name,
        current_date=datetime.now().strftime('%d_%m_%Y')
    )
    export_data_to_excel(data, path, filename)


def make_recrawl_base(project_name: str, path: str, indexed_pages: set, pages_in_sitemap: set) -> None:
    data = get_recrawl_base_data(indexed_pages, pages_in_sitemap)
    filename = f'{project_name}.xlsx'
    export_data_to_excel(data, path, filename)


def main():
    user_id = get_user_id()

    for site in get_sites():
        host, sitemap, project_name = site['host'], site['sitemap'], site['name']

        indexed_pages = get_indexed_pages(user_id, host)
        pages_in_sitemap = parse_sitemap(sitemap)

        make_visual_report(project_name, config.VISUAL_REPORTS_DIR, indexed_pages, pages_in_sitemap)
        make_recrawl_base(project_name, config.RECRAWL_BASES_DIR, indexed_pages, pages_in_sitemap)


if __name__ == '__main__':
    main()
