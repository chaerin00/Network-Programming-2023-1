import csv

import requests
from bs4 import BeautifulSoup
from flask import (Flask, request)

app = Flask(__name__)


def save_csv_data(rows):
    with open('solution2_csv.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)


def scrape_member_details(url):
    # Send a GET request to the website
    response = requests.get(url)

    soup = BeautifulSoup(response.content, 'html.parser')

    rows = []
    # it contains one or two members
    members = soup.find_all(class_="mYVXT")
    for member in members:
        image_elements = member.find_all('img')
        images = []
        for image in image_elements:
            images.append(image['src'])

        paragraphs = member.find_all(class_="hJDwNd-AhqUyc-II5mzb")
        for p in paragraphs:
            text = p.text
            if "(" in text and (")Research Interests:" in text or "@" in text):
                print('text---------------------\n', text)
                name, text = text.split("(", 1)
                role, text = text.split(",", 1)
                text = text.split('-', 1)
                start_year = None
                if len(text) == 2:
                    start_year = text[0]
                    text = text[1]
                else:
                    text = text[0]
                end_year, text = text.split(")", 1)
                end_year = None if len(end_year) == 0 else end_year
                interests = None
                current_job_role = None
                if "Research Interests:" in text:
                    _, interests = text.split('Research Interests:', 1)
                elif "@" in text:
                    current_job_role, _ = text.split('@', 1)
                row = [name, role, start_year, end_year, interests, current_job_role]
                if len(images) > 0:
                    row.append(images.pop())
                rows.append(row)

    save_csv_data(rows)
    return 'success'


@app.route('/member')
def home():
    # URL of the website to scrape
    url = "https://sites.google.com/view/davidchoi/home/members"
    args = request.args
    print(args.to_dict())
    # Call the scraper function
    result = scrape_member_details(url)
    print(result)

    return result


if __name__ == '__main__':
    app.run()
