from telethon.sync import TelegramClient
from telethon.functions import contacts
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.channels import GetFullChannelRequest
import string
import csv
from itertools import product
import numpy as np
import multiprocessing

with open('words.txt', "r") as file:
    keys = file.read().splitlines()
    
with open('tokens.txt', "r") as file:
    tokens = file.read().splitlines()

lowercase_alpha = string.ascii_lowercase

def print_info(type, title, query, description, count = None):
    print("TYPE:", type)
    print("TITLE:", title)
    print("KEY:", query)
    print("DESCRIPTION:", description)
    print("PARTICIPANTS:", count)
    print()
    
def write_data(data):
    with open("data.csv", 'a', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(data)

def app(combinations, api_id, api_hash):
    client = TelegramClient('parser_bot', api_id, api_hash)
    # client.set_proxy()
    client.start()
    
    try:
        for key, letter in combinations:
            query = f"{key} {letter}"
            print(query)
            result = client(contacts.SearchRequest(
                q=query,
                limit=100,
            ))
            
            if result.chats == [] and result.users == []: continue
            
            for chat in result.chats:
                description = client(GetFullChannelRequest(channel=chat)).full_chat.about
                data = ["chat", chat.title, query, description, chat.participants_count]
                print_info(*data)
                write_data(data)

            for user in result.users:
                if user.bot:
                    description = client(GetFullUserRequest(user.id)).full_user.about
                    data = ["bot", user.first_name, query, description]
                    print_info(*data)
                    write_data(data)
    except KeyboardInterrupt:
        print("stopping")
        client.disconnect()

def main():
    combinations = [item for item in product(keys, lowercase_alpha)]    
    split = np.array_split(combinations, len(tokens))
    
    params_list = []
    for i, part in enumerate(split):
        api_id, api_hash = tokens[i].split(':')
        params_list.append((part, api_id, api_hash))

    pool = multiprocessing.Pool(processes=len(tokens))
    pool.starmap(app, params_list)
    pool.close()
    pool.join()
    
if __name__ == "__main__":
    main()