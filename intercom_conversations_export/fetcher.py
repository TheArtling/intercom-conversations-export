from pathlib import Path
import datetime
import json
import os
import requests

from settings import OUTPUT_PATH, INTERCOM_TOKEN

LOCAL_TIMEZONE = datetime.datetime.now(
    datetime.timezone.utc).astimezone().tzinfo

headers = {
    'Authorization': 'Bearer ' + INTERCOM_TOKEN,
    'Accept': 'application/json'
}


def create_folders():
    single_conversations_path = os.path.join(OUTPUT_PATH, 'raw_data',
                                             'single_conversations')
    conversation_pages_path = os.path.join(OUTPUT_PATH, 'raw_data',
                                           'conversation_pages')

    if not os.path.exists(single_conversations_path):
        os.makedirs(single_conversations_path)
        print(f"Created {single_conversations_path}")

    if not os.path.exists(conversation_pages_path):
        os.makedirs(conversation_pages_path)
        print(f"Created {conversation_pages_path}")


def check_rate_limit(resp):
    print(resp.headers['X-RateLimit-Remaining'])
    if int(resp.headers['X-RateLimit-Remaining']) < 20:
        print("Sleeping for 10 seconds")
        sleep(10)


def write_conversations(data, page):
    path = os.path.join(OUTPUT_PATH, 'raw_data', 'conversation_pages', f"page_{page}.json")
    print(f"Writing page {page} to file")
    with open(path, 'w') as file:
        json.dump(data, file)


def get_first_page():
    resp = requests.get(
        "https://api.intercom.io/conversations?order=desc&sort=updated_at",
        headers=headers)
    if resp:
        print("Success! Getting conversations from page 1")
    data = resp.json()
    page = data['pages']['page']
    total_pages = data['pages']['total_pages']
    check_rate_limit(resp)

    return data, page, total_pages


def get_new_page_url(data):
    next_page_url = data['pages']['next']
    return next_page_url


def get_next_pages(next_page_url):
    resp = requests.get(next_page_url, headers=headers)
    data = resp.json()
    current_page = data['pages']['page']
    total_pages = data['pages']['total_pages']
    if data:
        print(f"Retrieving {current_page} of {total_pages}")
    check_rate_limit(resp)
    return data, current_page


def run_all_conversations():
    create_folders()
    data, page, total_pages = get_first_page()
    write_conversations(data, page)

    while (page < total_pages):
        next_page_url = get_new_page_url(data)
        data, page = get_next_pages(next_page_url)
        write_conversations(data, page)


def get_conversation_ids(data):
    conversations = data['conversations']
    conversation_ids = []
    for conversation in conversations:
        conversation_ids.append(conversation['id'])
    return conversation_ids


def get_single_conversation(id):
    print(f"Requesting id: {id}")
    url = 'https://api.intercom.io/conversations/' + id
    resp = requests.get(url, headers=headers)
    check_rate_limit(resp)
    data = resp.json()

    return data


def run_all_single_conversations():
    directory = os.path.join(OUTPUT_PATH, 'raw_data', 'conversation_pages')
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        with open(file_path) as json_file:
            data = json.load(json_file)
            conversation_ids = get_conversation_ids(data)

        for id in conversation_ids:
            data = get_single_conversation(id)
            path = os.path.join(OUTPUT_PATH, 'raw_data', 'single_conversations', f"id_{id}.json")
            print(f"Writing {id} to file")
            with open(path, 'w') as file:
                json.dump(data, file)


run_all_conversations()
run_all_single_conversations()
