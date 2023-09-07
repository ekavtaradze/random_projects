import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from zipfile import ZipFile


def download_and_unzip_files(zip_file_name, href):

    data_directory_name = os.getenv('data_directory_name')
    zip_directory_name = os.getenv('zip_directory_name')
    download_url_prefix = os.getenv('download_url_prefix')

    zip_url = f"{download_url_prefix}{href}"

    zip_destination_name = f"{zip_directory_name}/{zip_file_name}"

    zip_response = requests.get(zip_url)
    if zip_response.status_code == 200:

        with open(zip_destination_name, "wb") as zip_file:
            zip_file.write(zip_response.content)
            print(f"Downloaded: {zip_file_name}")

        with ZipFile(zip_destination_name, 'r') as zip_ref:
            zip_ref.extractall(data_directory_name)
            print(f"Unzipped: {zip_file_name}")
    else:
        print(f"Failed to download: {zip_url}")


def get_zip_name(row):
    possible_name_td = row.find('td', {'class': 'labelOptional_ind'})
    text = possible_name_td.get_text(strip=True) if possible_name_td else None
    name = text if text and '.zip' in text else None
    return name


def get_zip_link(row):
    possible_link_tds = row.find_all(
        'td', {'class': 'labelOptional'}, recursive=False)
    link_href = None
    for link_td in possible_link_tds:
        link = link_td.find('a')
        if link:
            link_href = link.get('href')
    return link_href


def find_rows_with_zip_data(table):
    rows = table.find_all('tr', recursive=True)
    for row in rows:
        name = get_zip_name(row)
        link = get_zip_link(row)

        if name and link:
            download_and_unzip_files(name, link)


def do_scraping(url):
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the page
        page = BeautifulSoup(response.text, "html.parser")

        find_rows_with_zip_data(page)

    else:
        print(f"Failed to fetch the webpage: {url}")


def make_directory(name):
    # Create a directory to store the downloaded zip files
    os.makedirs(name, exist_ok=True)


def read_all_sheets(file_path):
    xls = pd.ExcelFile(file_path)
    sheet_dfs = []
    for sheet in xls.sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet)
        sheet_dfs.append(df)
    return sheet_dfs


def read_all_files(directory_name):
    file_dfs = []
    for file_name in os.listdir(directory_name):
        full_path = f"{directory_name}/{file_name}"
        print(full_path)
        if full_path.endswith('.xlsx'):
            sheets = read_all_sheets(full_path)
            file_dfs += sheets
    return file_dfs


def do_very_specific_finding(directory_name):

    dfs = read_all_files(directory_name)
    combined_df = pd.concat(dfs, ignore_index=True)

    location_filter_df = combined_df[combined_df['Settlement Point Name'] == 'HB_WEST']

    necessary_cols_df = location_filter_df[[
        'Delivery Date', 'Settlement Point Price']]
    necessary_cols_df['Month Year'] = pd.to_datetime(
        necessary_cols_df['Delivery Date']).dt.strftime('%m-%Y')
    necessary_cols_df = necessary_cols_df[[
        'Month Year', 'Settlement Point Price']]

    agg_df = necessary_cols_df.groupby(['Month Year'])[
        'Settlement Point Price'].mean()

    final_filter = agg_df[agg_df > 100]
    print(final_filter.describe)
