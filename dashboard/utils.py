import os
from psycopg2 import extras, connect
from datetime import timedelta, datetime
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')


def connection():
    conn = connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    return conn


def get_user_by_id(user_id: int):
    conn = connection()
    cur = conn.cursor(cursor_factory=extras.DictCursor)
    cur.execute("SELECT name, last_name FROM users WHERE external_id = %s", (user_id,))
    user = cur.fetchone()
    if user is None:
        return None
    conn.close()
    return f'{user[0]} {user[1]}'


def get_active_deals_count(user_id):
    conn = connection()
    cur = conn.cursor(cursor_factory=extras.DictCursor)
    today = (datetime.now() - timedelta(days=40)).replace(hour=0, minute=0, second=0, microsecond=0)
    format_string = "%Y-%m-%d %H:%M:%S"
    cur.execute("select * from deal where date_modify > %s and assigned_by_id = %s",
                (today.strftime(format_string), user_id))
    active_deals = cur.fetchall()
    return len(active_deals)


def get_all_deals_per_user(deals: list, user_id=int):
    deal_count = 0
    for deal in deals:
        for key, value in deal.items():
            if key == 'assigned_by_id' and value == user_id:
                deal_count += 1
    return deal_count


def get_deals():
    conn = connection()
    cur = conn.cursor(cursor_factory=extras.DictCursor)
    today = (datetime.now() - timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
    format_string = "%Y-%m-%d %H:%M:%S"
    cur.execute("SELECT * FROM deal WHERE date_create > %s", (today.strftime(format_string),))
    deals = cur.fetchall()
    data = {}
    for deal in deals:
        for key, val in deal.items():
            if key == 'closed' and val == 'N':
                if deal['assigned_by_id'] not in data:
                    data[deal['assigned_by_id']] = []
                temp = {
                    'opportunity': deal['opportunity']
                }
                data[deal['assigned_by_id']].append(temp)

    updated_data = []
    all_deals = 0
    for key, val in data.items():
        user = get_user_by_id(key)
        if user is None:
            user = 'unknown'
        opportunity, opportunity_count = 0, 0
        for value in val:
            if value['opportunity'] > 0.0:
                opportunity_count += 1
            opportunity += value['opportunity']
            all_deals += 1
        new_val = {
            'responsible_user': user,
            'sales_price': int(opportunity),
            'average_check': round(int(opportunity) / opportunity_count if opportunity_count > 0 else 0, 1),
            'conversion': round((opportunity_count / all_deals if opportunity_count > 0 and all_deals > 0 else 0) * 100,
                                1),
            'sales_count': opportunity_count,
            'new_deals': get_all_deals_per_user(deals, key),
            'leads': get_active_deals_count(key)
        }

        updated_data.append(new_val)

    conn.close()
    return updated_data
