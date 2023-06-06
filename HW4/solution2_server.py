import csv

import requests
from bs4 import BeautifulSoup
from flask import (Flask, request, jsonify)

app = Flask(__name__)


def find_member(target_name):
    result = []
    # Open the CSV file and read its contents
    with open('solution2_csv.csv', 'r') as file:
        csv_reader = csv.reader(file)

        # Iterate over each row in the CSV file
        for row in csv_reader:
            name = row[0]  # Assuming the name is in the first column

            # Check if the name matches the target name
            if target_name in name:
                result.append(row)
    return result


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
    query = args.to_dict()
    # Call the scraper function
    scrape_member_details(url)
    searched_members = find_member(query['name'])
    response_data = []
    for member in searched_members:
        member_response = {
            "name": member[0],
            "job_role": member[1],
            "start_year": member[2],
            # place NA for missing value
            "end_year": member[3] if len(member[3]) > 0 else "NA",
            "research_interest": member[4] if len(member[4]) > 0 else "NA",
            "current_job_role": member[5] if len(member[5]) > 0 else "NA",
            "profile_pic_url": member[6] if len(member[6]) > 0 else "NA"
        }
        response_data.append(member_response)

    return jsonify(response_data)


if __name__ == '__main__':
    app.run()
