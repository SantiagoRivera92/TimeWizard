import urllib.request
import json
import sys
import datetime

from os import walk
import os
import hashlib

header= {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) ' 
            'AppleWebKit/537.11 (KHTML, like Gecko) '
            'Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}

with open("static/ignored_dates.json", "r", encoding="utf-8") as file:
    ignored_dates = json.load(file)
    
with open("static/ignored_sets.json", "r", encoding="utf-8") as file:
    ignored_sets = json.load(file)

with open("static/exclusions.txt", "r", encoding="utf-8") as file:
    anime_shit = file.read()
    
with open("static/popular_formats.json", "r", encoding="utf-8") as file:
    popular_formats = json.load(file)

# Cache the sets call in order to reduce load times
cached_sets = []
cached_cards = []


def date_from_string(date_as_string):
    year = int(date_as_string[0:4])
    month = int(date_as_string[5:7])
    day = int(date_as_string[8:10])
    return datetime.datetime(year, month, day)

def get_full_set_list():
    global cached_sets
    if len(cached_sets) == 0:
        sets_url = "https://db.ygoprodeck.com/api/v7/cardsets.php"
        sets_request = urllib.request.Request(sets_url, None, header)
        with urllib.request.urlopen(sets_request) as url:
            cached_sets = json.loads(url.read().decode())
            cached_sets = [set_item for set_item in cached_sets if set_item.get('tcg_date') != "0000-00-00"]
    return cached_sets

def get_set_list(date):
    sets = get_full_set_list()
    legal_sets = [
        tcg_set['set_name'] for tcg_set in sets
        if tcg_set.get('tcg_date') != "0000-00-00" and date_from_string(tcg_set['tcg_date']) <= date
        and tcg_set['set_code'] not in ignored_dates
    ]
    return list(dict.fromkeys(legal_sets))

def find_banlist(date):
    filenames = get_banlist_file_names()
    lastbanlist = "2002-03-01.json"
    for filename in filenames:
        banlist_date = date_from_string(filename)
        if banlist_date > date:
            break
        lastbanlist = filename

    return lastbanlist

def get_banlist_file_names():
    filenames = next(walk("banlists"), (None, None, []))[2]
    return filenames

def get_banlist_object(banlist_file):
    with open(f"banlists/{banlist_file}", encoding="utf-8") as json_file:
        banlist = json.load(json_file)
        json_file.close()
        return banlist

def test_banlists():
    cards = download_cards()
    for filename in get_banlist_file_names():
        banlist = get_banlist_object(filename)
        not_found_cards = []
        #Test all forbidden cards
        for forbidden_card in banlist.get('forbidden'):
            if not is_card_in_banlist(forbidden_card, cards):
                not_found_cards.append(forbidden_card)
        for limited_card in banlist.get('limited'):
            if not is_card_in_banlist(limited_card, cards):
                not_found_cards.append(limited_card)
        for semilimited_card in banlist.get('semilimited'):
            if not is_card_in_banlist(semilimited_card, cards):
                not_found_cards.append(semilimited_card)
        if len(not_found_cards) > 0:
            print(filename)
            print(not_found_cards)

def is_card_in_banlist(banlist_card, cards):
    found = False
    for card in cards:
        if banlist_card == card['name']:
            found = True
    return found

def download_cards():
    global cached_cards
    if len(cached_cards) == 0:
        cards_url = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
        cards_request = urllib.request.Request(cards_url, None, header)
        with urllib.request.urlopen(cards_request) as url:
            cached_cards = json.loads(url.read().decode()).get('data')
    return cached_cards

def get_card_list(set_list, banlist_file):
    banlist = get_banlist_object(banlist_file)
    cards = download_cards()
    card_list = []
    for card in cards:
        if card.get('card_sets') is not None and any(
            card_set['set_name'] in set_list for card_set in card['card_sets']
        ):
            banlist_status = next(
                (i for i, lst in enumerate([banlist['forbidden'], banlist['limited'], banlist['semilimited']]) if card['name'] in lst), 3
            )
            simple_card = {
                'name': card['name'],
                'id': [variant['id'] for variant in card.get('card_images', [{'id': card['id']}])],
                'status': banlist_status
            }
            card_list.append(simple_card)
    return card_list

def print_cards(card_list, date, name, curated):
    filename_prefix = f"{date.year:04d}-{date.month:02d}-{date.day:02d}"
    filename_suffix = f" ({name})" if name else ""
    filename = f"{filename_prefix}{filename_suffix}.lflist.conf"

    if curated:
        directory = "curated"
    elif name != "Advanced":
        directory = "all lists"
    else:
        directory = None
    
    if directory:
        filename = f"lflist/{directory}/{filename}"
    else:
        filename = f"lflist/{filename}"

    with open(filename, 'w', encoding="utf-8") as outfile:
        outfile.write(f"#[{name} format]\n" if name else f"#[{date.year:04d}-{date.month:02d}-{date.day:02d}]\n")
        outfile.write(f"!{filename_prefix}{filename_suffix}\n")
        outfile.write("$whitelist\n")
        outfile.write(anime_shit)
        outfile.write("\n")
        for card in card_list:
            for card_id in card['id']:
                line = f"{card_id} {card.get('status')}-- {card.get('name')}\n"
                outfile.write(line)


def generate_banlist(date, name, curated):
    if name != "F&L":
        print(f"Generating {name} banlist")
    else:
        print(f"Generating {get_date_as_string(date)} Forbidden and Limited List update banlist")
    sys.stdout.flush()
    banlist_file = find_banlist(date)
    set_list = get_set_list(date)
    card_list = get_card_list(set_list, banlist_file)
    print_cards(card_list, date, name, curated)

def clear_banlist_folder():
    for _, _, files in walk("lflist/all lists"):
        for filename in files:
            os.remove(f"lflist/all lists/{filename}")
    for _,_, files in walk("lflist/curated"):
        for filename in files:
            os.remove(f"lflist/curated/{filename}")

def generate_all_lists():
    calculate = True
    if calculate:
        clear_banlist_folder()
        banlist_dates = {(date_from_string(filename), "F&L") for filename in get_banlist_file_names()}
        release_dates = {
            (date_from_string(card_set.get('tcg_date')),
            card_set.get('set_code') + " Special Edition" if "Special Edition" in card_set.get('set_name') else card_set.get('set_code'))
            for card_set in get_full_set_list()
            if card_set.get('tcg_date') != "0000-00-00" and
            date_from_string(card_set.get('tcg_date')) >= datetime.datetime(2002, 3, 8) and
            card_set.get('tcg_date') not in ignored_dates and card_set.get('set_code') not in ignored_sets
            and not "Premiere!" in card_set.get('set_name') and not "Sneak Peek" in card_set.get('set_name')
        }   

        good_dates = sorted((banlist_dates | release_dates), reverse=True)
        
        # Remove duplicate dates and combine set names if duplicates are found
        unique_dates = {}
        for date, set_code in good_dates:
            if date in unique_dates:
                existing_date = unique_dates[date]
                if existing_date != "F&L":
                    if set_code != "F&L":
                        unique_dates[date] += f", {set_code}"
                    else:
                        unique_dates[date] = "F&L"
            else:
                unique_dates[date] = set_code

        # Update good_dates with unique dates and combined set names
        good_dates = [(date, set_code) for date, set_code in unique_dates.items()]

        most_recent = good_dates[0]
        generate_banlist(most_recent[0], "Advanced", False)

        count = len(good_dates)

        for i, (date, set_code) in enumerate(good_dates):
            generate_banlist(date, set_code, False)
            print(f"{i} / {count}, {(i * 100 / count):2f}% done")

    print("Proactively handling duplicates...", flush=True)

    duplicates = find_duplicates()
    for file_pair in duplicates:
        file_path1, file_path2 = file_pair
        file_path1 = file_path1.replace(".lflist", "")
        file_path2 = file_path2.replace(".lflist", "")
        date2 = file_path2.split()[0]
        os.remove(f"lflist/all lists/{file_path2}.lflist.conf")
        ignored_dates.append(date2)
        print(f"Duplicate found: {file_path2}")
        
    with open("static/ignored_dates.json", "w", encoding="utf-8") as outfile:
        json.dump(ignored_dates, outfile)

def get_date_as_string(date):
    return f"{date.year:04d}-{date.month:02d}-{date.day:02d}"

def generate_popular_lists():
    for ygoformat in popular_formats:
        format_name = ygoformat.get("name")
        format_date = ygoformat.get("date")
        generate_banlist(date_from_string(format_date), format_name, True)

def calculate_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as hash_file:
        for _ in range(2):  
            hash_file.readline()
        buf = hash_file.read(4096)
        while len(buf) > 0:
            hasher.update(buf)
            buf = hash_file.read(4096)
    return hasher.hexdigest()

def find_duplicates():
    file_hashes = {}
    duplicates = []
    for root, _, files in walk("lflist/all lists"):
        for filename in files:
            file_path = os.path.join(root, filename)
            file_hash = calculate_hash(file_path)
            if file_hash in file_hashes:
                duplicates.append((file_hashes[file_hash], os.path.splitext(filename)[0]))
            else:
                file_hashes[file_hash] = os.path.splitext(filename)[0]
    return [(f1.replace(".lflist", ""), f2.replace(".lflist", "")) for f1, f2 in duplicates if "JUMP" not in (f1, f2)]

generate_all_lists()
generate_popular_lists()