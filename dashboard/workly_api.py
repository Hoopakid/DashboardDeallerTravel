import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

BASE_URL = 'https://api.workly.uz/v1/'

email = os.environ.get('EMAIL')
password = os.environ.get('PASSWORD')
client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLIENT_SECRET')


def authorize_user():
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    data = {
        'client_secret': client_secret,
        'client_id': client_id,
        'grant_type': 'password',
        'username': email,
        'password': password
    }
    url = BASE_URL + 'oauth/token'
    response = requests.post(url, data=data, headers=headers)
    if response.status_code == 200:
        return {"success": True, "data": response.json()}
    return {"success": False}


def get_in_out_info():
    url = BASE_URL + 'reports/inouts'
    authorize = authorize_user()

    if authorize['success'] == False:
        return {"success": False}

    token = authorize['data']['access_token']
    headers = {
        'authorization': f'Bearer {token}'
    }

    yesterday_date = (datetime.now() - timedelta(days=1)).date()
    today_date = datetime.now().date()
    # timed_url = url + f'?start_date={yesterday_date}&end_date={today_date}'
    timed_url = url + f'?start_date={today_date}&end_date={today_date}'

    response = requests.get(timed_url, headers=headers)
    if response.status_code == 200:
        return {"success": True, "data": response.json()}
    return {"success": False}


def subtract_out_from_in(out_time, in_time):
    time_format = "%H:%M"

    out_time_dt = datetime.strptime(out_time, time_format)
    in_time_dt = datetime.strptime(in_time, time_format)

    time_difference = out_time_dt - in_time_dt

    if time_difference.total_seconds() < 0:
        time_difference += timedelta(days=1)

    total_seconds = int(time_difference.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    result = f"{hours:02}:{minutes:02}"

    return result


def latin_to_krill_convert(name: str):
    url = 'https://deep-translator-api.azurewebsites.net/'
    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        'source': 'ru',
        'target': 'uz',
        'text': name,
        'proxies': []
    }
    response = requests.post(url + 'google', headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['translation']
    return name


def by_users():
    data = get_in_out_info()
    if data['success'] == False:
        return {"success": False}
    users = data['data']['items']
    ctx = {}
    for user in users:
        user_name = latin_to_krill_convert(user['first_name']).lower()
        if user['position_title'] == 'Авиа кассир':
            if user_name not in ctx:
                ctx[user_name] = {
                    'in': '',
                    'out': ''
                }
            if 'in' == user['event_name']:
                time = user['event_time'].split(':')
                ctx[user_name]['in'] = f'{time[0]}:{time[1]}'
            elif 'out' == user['event_name']:
                time_ = user['event_time'].split(':')
                ctx[user_name]['out'] = f'{time_[0]}:{time_[1]}'

    for user, val in ctx.items():
        if val['in'] and val['out']:
            val.update({'all': subtract_out_from_in(val['out'], val['in'])})
        elif val['in']:
            current_time = datetime.now().strftime("%H:%M")
            val.update({'all': subtract_out_from_in(current_time, val['in'])})
        else:
            val.update({'all': '00:00'})

    return ctx
