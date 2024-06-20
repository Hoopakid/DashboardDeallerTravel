import logging, os, asyncio, pandas as pd, requests, re

from time import sleep
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
from dotenv import load_dotenv

from fuzzywuzzy import fuzz, process
import transliterate

load_dotenv()

USERNAME = os.environ.get('USER_USERNAME')
PASSWORD = os.environ.get('PASSWORD')

def get_token():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto('https://panel.strawberryhouse.uz/login')
        username = page.get_by_placeholder("Логин")
        username.fill(USERNAME)

        password = page.get_by_placeholder('Пароль')
        password.fill(PASSWORD)

        page.get_by_role('button').click()
        today = datetime.now().date()
        sleep(3)
        last_day_url = f'https://panel.strawberryhouse.uz/statistics/operators?start={today}+00%3A00&end={str(today)}+23%3A59'
        page.goto(last_day_url)

        page.wait_for_selector('table')
        rows = page.query_selector_all('table tbody tr')
        datas = []
        for r in rows:
            row = r.query_selector_all('td')
            data =  [td.text_content() for td in row]
            if data[-1].endswith('сум'):
                temp = {
                    data[1]: {
                        'sales_count': int(data[6].replace(' шт', '').replace(' ', '')),
                        'sales_price': int(data[7].replace(' сум', '').replace(' ', ''))
                    }}
                datas.append(temp)
    browser.close()
    return datas

def prepare_params(params, prev=""):
    """Transforms list of params to a valid bitrix/amocrm array."""
    ret = ""
    if isinstance(params, dict):
        for key, value in params.items():
            if isinstance(value, dict):
                if prev:
                    key = "{0}[{1}]".format(prev, key)
                ret += prepare_params(value, key)
            elif (isinstance(value, list) or isinstance(value, tuple)) and len(
                    value
            ) > 0:
                for offset, val in enumerate(value):
                    if isinstance(val, dict):
                        ret += prepare_params(
                            val, "{0}[{1}][{2}]".format(prev, key, offset)
                        )
                    else:
                        if prev:
                            ret += "{0}[{1}][{2}]={3}&".format(prev, key, offset, val)
                        else:
                            ret += "{0}[{1}]={2}&".format(key, offset, val)
            else:
                if prev:
                    ret += "{0}[{1}]={2}&".format(prev, key, value)
                else:
                    ret += "{0}={1}&".format(key, value)
    return ret


def get_amocrm_staff(token, url, select=[]):
    header = {'Authorization': f"Bearer {token}"}
    resp = requests.get(url+'users', headers=header)
    if resp.status_code==401:
        return {'unauthorized':True}
    r = resp.json()['_embedded']['users']

    while resp.json()['_links'].get('next', False):
        resp = requests.get(resp.json()['_links']['next']['href'], headers=header)
        if resp.status_code==204: break
        r.extend(resp.json()['_embedded']['users'])
    if not select:
        return r

    r = [{key:val for key, val in i.items() if key in select} for i in r]
    return r
def get_amocrm_leads(token, url,
              start_date: int,
              end_date: int,
              type='created_at',
              params={},
    ):
    params['filter'] = {} if not params.get('filter') else params['filter']
    params['filter'][type] = {
        'from': start_date,
        'to': end_date
    }
    # print(prepare_params(params))
    header = {'Authorization': f"Bearer {token}"}
    resp = requests.get(url+'leads', params=prepare_params(params), headers=header)

    if resp.status_code==401:
        return {'unauthorized':True}
    elif resp.status_code==204:
        return pd.DataFrame()

    r = resp.json()['_embedded']['leads']

    while resp.json()['_links'].get('next', False):
        resp = requests.get(resp.json()['_links']['next']['href'], headers=header)
        if resp.status_code==204: break
        r.extend(resp.json()['_embedded']['leads'])

    # EXTRAS
    users = get_amocrm_staff(token, url)
    for i in r:
        for s in users:
            if i.get('responsible_user_id') == s.get('id'):
                i['responsible_user'] = normalize_name(s.get('name'))

    r = pd.DataFrame(r)
    return r


def transliterate_name(name):
    try:
        return transliterate.translit(name, reversed=True)
    except:
        return name

def remove_numbers(name):
    return re.sub(r'\d+', '', name).strip()

def normalize_name(name):
    name = remove_numbers(name)
    name = transliterate_name(name)
    return name

def find_best_match(name, choices):
    match, score = process.extractOne(name, choices)
    return match if score > 80 else None  # Adjust threshold as needed


def get_cookie_by_key(cookies, key):
    for cookie in cookies:
        if cookie['name'] == key:
            return cookie['value']
    return None


def get_token():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto('https://panel.strawberryhouse.uz/login')
        username = page.get_by_placeholder("Логин")
        username.fill(USERNAME)

        password = page.get_by_placeholder('Пароль')
        password.fill(PASSWORD)

        page.get_by_role('button').click()
        sleep(3)
        cookies = context.cookies()
        cookie = get_cookie_by_key(cookies, '_identity-backend')
        browser.close()
    return cookie

