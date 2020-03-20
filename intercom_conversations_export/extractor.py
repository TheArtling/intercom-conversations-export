from bs4 import BeautifulSoup
from urllib.parse import urlparse
import datetime
import json
import os
import requests

from settings import OUTPUT_PATH

LOCAL_TIMEZONE = datetime.datetime.now(
    datetime.timezone.utc).astimezone().tzinfo


def parse_timestamp(ts, format):
    time = datetime.datetime.fromtimestamp(ts,
                                           tz=LOCAL_TIMEZONE).strftime(format)
    return time


def get_folder_name(convo):
    if convo['source']['delivered_as'] == "automated":
        author = convo['conversation_parts']['conversation_parts'][0]['author']
    else:
        author = convo['source']['author']
    author_email = author['email']
    author_id = author['id']
    folder_name = author_email if author_email else author_id
    return folder_name


def check_for_image(body, folder_path):
    soup = BeautifulSoup(body, "html5lib")
    try:
        image_link = soup.img['src']
        path = urlparse(image_link).path
        title = os.path.split(
            os.path.dirname(path))[1] + "--" + os.path.basename(path)
        print(f"getting image {title}")
        image_file_path = os.path.join(folder_path, title)
        if not os.path.exists(image_file_path):
            resp = requests.get(image_link)
            with open(image_file_path, 'wb') as file:
                file.write(resp.content)
            return title
    except:
        return


def get_file_name(convo):
    ts = convo['created_at']
    time = parse_timestamp(ts, '%Y_%m_%d_%I_%M_%p')
    return time


def parse_body(body, folder_path):
    image_title = check_for_image(body, folder_path)
    soup = BeautifulSoup(body, 'html5lib')
    parsed_body = soup.get_text()
    if soup.a:
        link_array = []
        links = soup.findAll('a')
        for link in links:
            try:
                href = link['href']
                link_array.append(href)
            except:
                continue
        link_str = ', '.join(link_array)
        link = f" ({link_str})"
        parsed_body = parsed_body + link
    if image_title:
        parsed_body = "[Image " + image_title + "]"
    return parsed_body


def parse_author(author_dict):
    name = author_dict['name']
    email = author_dict['email']
    author_type = author_dict['type']

    author_detail = name if name else email
    if author_detail:
        author = author_detail + " - " + author_type
        return author
    return author_type.capitalize()


def parse_conversation(convo, folder_path):
    text_array = []

    text_array.append(f"Conversation ID: {convo['id']}")

    ts = convo['created_at']
    started_time = parse_timestamp(ts, "%B %d, %Y at %I:%M %p %Z")

    text_array.append(f"Started on {started_time}")

    url = convo['source']['url']
    if url:
        text_array.append(f"Landed on {url}")

    subject = convo['source']['subject']
    if subject:
        soup = BeautifulSoup(subject, 'html5lib')
        subject = soup.get_text()
        text_array.append(subject)

    text_array.append("---\n")

    body = convo['source']['body']
    if body:
        body = parse_body(body, folder_path)

    time = parse_timestamp(ts, '%d/%m/%Y %H:%M %p')

    author_dict = convo['source']['author']
    author = parse_author(author_dict)

    message = f"{time} | {author} : {body}"

    text_array.append(message)

    parts = convo['conversation_parts']['conversation_parts']
    parts_array = []
    for part in parts:
        ts = part['created_at']
        time = parse_timestamp(ts, '%d/%m/%Y %H:%M %p')

        author_dict = part['author']
        author = parse_author(author_dict)

        body = part['body']
        if body:
            body = parse_body(body, folder_path)
        else:
            body = "Action - " + part['part_type']

        message = f"{time} | {author} : {body}"

        parts_array.append(message)

    text_array = text_array + parts_array
    return text_array


def write_conversation_parts(txt_array, file_path):
    with open(file_path, 'w') as file:
        for line in txt_array:
            file.write(line + "\n")
    return


def run():
    raw_conversations_path = os.path.join(OUTPUT_PATH, 'raw_data',
                                          'single_conversations')
    counter = 0
    all_convo_files = next(os.walk(raw_conversations_path))[2]
    total_convos = len(all_convo_files)

    for file in os.listdir(raw_conversations_path):
        counter += 1
        print(f"Writing file {counter} of {total_convos}")
        file_path = os.path.join(raw_conversations_path, file)
        with open(file_path) as json_file:
            convo = json.load(json_file)
        folder_name = get_folder_name(convo)
        folder_path = os.path.join(OUTPUT_PATH, 'conversations', folder_name)
        try:
            os.makedirs(folder_path)
            print(f"{folder_name} created")
        except OSError as error:
            print(f"{folder_name} already exists")

        file_name = get_file_name(convo)
        file_path = os.path.join(folder_path, f"{file_name}.txt")
        if not os.path.exists(file_path):
            text_array = parse_conversation(convo, folder_path)
            write_conversation_parts(text_array, file_path)
        else:
            print(f"{file_path} already exists")


run()
