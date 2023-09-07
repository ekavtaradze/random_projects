import os
from utils import *
from dotenv import load_dotenv

load_dotenv()

data_directory_name = os.getenv('data_directory_name')
zip_directory_name = os.getenv('zip_directory_name')
source_url = os.getenv('source_url')


make_directory(zip_directory_name)
make_directory(data_directory_name)


do_scraping(source_url)

do_very_specific_finding(data_directory_name)