import os
import json
import requests
import datetime
from pathlib import Path

from settings import OUTPUT_PATH, INTERCOM_TOKEN

LOCAL_TIMEZONE = datetime.datetime.now(
    datetime.timezone.utc).astimezone().tzinfo

headers = {
    'Authorization': 'Bearer ' + INTERCOM_TOKEN,
    'Accept': 'application/json'
}

# make conversations folder if not already made
# os.makedirs('conversations')


def check_rate_limit(resp):
    print(resp.headers['X-RateLimit-Remaining'])
    if int(resp.headers['X-RateLimit-Remaining']) < 20:
        print("Sleeping for 10 seconds")
        sleep(10)


def write_conversations(data, page):
    path = os.path.join(OUTPUT_PATH, 'conversations', f"page_{page}.json")
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
    data, page, total_pages = get_first_page()
    write_conversations(data, page)

    while (page < total_pages):
        next_page_url = get_new_page_url(data)
        data, page = get_next_pages(next_page_url)
        write_conversations(data, page)


# run_all_conversations()


def get_conversation_ids(data):
    conversations = data['conversations']
    conversation_ids = []
    for conversation in conversations:
        conversation_ids.append(conversation['id'])
    return conversation_ids

    print(f"Requesting id: {conversation_ids[1]}")


def get_single_conversation(id):
    url = 'https://api.intercom.io/conversations/' + id
    print(f"Getting conversations from id: {id}")
    resp = requests.get(url, headers=headers)
    check_rate_limit(resp)

    return resp.json()


def parse_conversation_parts(convo):
    parts = convo['conversation_parts']['conversation_parts']
    parts_array = []
    import ipdb
    ipdb.set_trace()
    for part in parts:

        author = part['author']['name']
        if author == None:
            author = part['author']['id']
        author_type = part['author']['type']
        ts = part['created_at']
        time = datetime.datetime.fromtimestamp(
            ts, tz=LOCAL_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')
        body = part['body']
        message = f"---------------------------\n{time} \n{author} - {author_type} \n{body}\n"
        parts_array.append(message)

    return parts_array


def write_conversation_parts(parts):
    total_count = len(parts)
    output_path = os.path.join(OUTPUT_PATH, 'conversations', 'thing')
    with open(output_path, 'w') as file:
        file.write(f"Total parts: {total_count}\n")
        file.writelines(parts)
    return


def run_single_conversations():
    conversation_ids = get_conversation_ids(data)
    for id in conversation_ids:
        get_single_conversation(id)
        convo = get_single_conversation(id)
        parts = parse_conversation_parts(convo)
        write_conversation_parts(parts)


# file.write(resp.content)
# import json
# content = None
# with open('filename.json', 'r') as file:
#     content = file.read()

# data = json.loads(content)