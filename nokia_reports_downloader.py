import requests
from bs4 import BeautifulSoup
import os
import re

class NokiaReportDownloader:
    def __init__(self, base_url, output_dir):
        self.base_url = base_url
        self.output_dir = output_dir
        self.patterns = self._generate_patterns()

    def _generate_patterns(self):  
        patterns = {}
        for year in range(2019, 2024):
            year_in_str = str(year)
            if year == 2023 or year == 2022:
                patterns[year_in_str] = re.compile(fr"/system/files/\d{{4}}-\d{{2}}/nokia-annual-report-{year_in_str}\.pdf")
            elif year == 2021:
                patterns[year_in_str] = re.compile(r"/system/files/\d{4}-\d{2}/nokia-ar21-en\.pdf")
            elif year == 2020:
                patterns[year_in_str] = re.compile(r"/system/files/\d{4}-\d{2}/Nokia_Annual_Report_2020_English\.pdf")
            elif year == 2019:
                patterns[year_in_str] = re.compile(r"/system/files/\d{4}-\d{2}/Nokia%20in%202019%20annual%20report_1\.pdf")
        return patterns


    def fetch_pdf_links(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
        }
        try:
            response = requests.get(self.base_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            found_links = soup.find_all('a', href=True)
            pdf_links = []

            for link in found_links:
                href = link['href']
               
                for year in self.patterns:
                    pattern = self.patterns[year]
                    if pattern.match(href):
                        full_url = f"https://www.nokia.com{href}"
                        pdf_links.append(full_url)
                        break

            return pdf_links
        except requests.exceptions.RequestException as e:
            return []

    def download_pdf(self, pdf_url):
        try:
            report_name = pdf_url.split("/")[-1]
            file_path = os.path.join(self.output_dir, report_name)

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
            }
            pdf_response = requests.get(pdf_url, headers=headers)
            pdf_response.raise_for_status()

            with open(file_path, 'wb') as file:
                file.write(pdf_response.content)
            print(f"Downloaded: {report_name}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {pdf_url}: {e}")

    def download_reports(self):
        os.makedirs(self.output_dir, exist_ok=True)
        pdf_links = self.fetch_pdf_links()

        if not pdf_links:
            print("No PDF links found. Exiting.")
            return

        for link in pdf_links:
            self.download_pdf(link)

if __name__ == "__main__":
    BASE_URL = "https://www.nokia.com/about-us/investors/results-reports/#annual-reports"
    OUTPUT_DIR = "nokia_reports_yr_5"

    downloader = NokiaReportDownloader(BASE_URL, OUTPUT_DIR)
    downloader.download_reports()
