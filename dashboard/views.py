import os, pandas as pd, requests
from datetime import datetime
from pprint import pprint
from django.shortcuts import render
from fuzzywuzzy import process, fuzz

from .utils import find_best_match, normalize_name, remove_numbers, transliterate_name, get_token, get_amocrm_leads


PLAN = 5_000_000

# Create your views here.
def home(r):
    today = datetime.now()
    start_date_unix = int(today.replace(hour=0, minute=0, second=0).timestamp())
    end_date_unix = int(today.replace(hour=23, minute=59, second=59).timestamp())

    crm_data = get_amocrm_leads(os.environ.get('AMOCRM_TOKEN'), os.environ.get('AMOCRM_URL'), start_date_unix, end_date_unix, 'updated_at')
    crm_names = crm_data['responsible_user'].unique()
    print(crm_data.columns)
    print("CRM data fetched")

    try:
        token = get_token()
        cookies = {'_identity-backend': token}
        resp = requests.get(f"https://panel.strawberryhouse.uz/statistics/operators-excel?start={today.strftime('%Y-%m-%d')}+00%3A00&end={today.strftime('%Y-%m-%d')}+23%3A55", timeout=20, cookies=cookies)
        panel_data = pd.read_html(resp.content)
    except requests.exceptions.ReadTimeout:
        return render(r, 'home.html', context={'ok': False})
    panel_data=pd.DataFrame(panel_data[0])
    panel_data=panel_data.drop(columns="#")
    panel_data.rename(columns={'Имя':'name', 'Общ. кол.':'sales_count', 'Итого':'sales_price'}, inplace=True)
    print("Panel data fetched")

    panel_data.drop(columns=['Call Center', 'Сумма КЦ', 'Telegram', 'Сумма Бот'], inplace=True)
    panel_data['sales_count'] = panel_data['sales_count'].str.replace(r'[^\d]', '', regex=True).astype(int)
    panel_data['sales_price'] = panel_data['sales_price'].str.replace(r'[^\d]', '', regex=True).astype(int)
    panel_data['name'] = panel_data['name'].apply(lambda x: normalize_name(x))
    panel_data['name'] = panel_data['name'].apply(find_best_match, args=(crm_names,))
    
    by_staff_leads = crm_data.groupby('responsible_user').aggregate(leads=('id', 'count')).reset_index()
    new_leads = crm_data[crm_data['created_at'] > start_date_unix]
    by_staff_new_leads = new_leads.groupby('responsible_user').aggregate(new_leads=('id', 'count')).reset_index()
    by_staff_leads = pd.merge(by_staff_leads, by_staff_new_leads, on='responsible_user', how='left')
    print(by_staff_leads)


    merged = by_staff_leads.merge(panel_data, left_on="responsible_user", right_on='name')
    merged.drop(columns=['name'], inplace=True)
    merged['conversion'] = round(merged['sales_count']/merged['leads']*100)
    merged['plan'] = round(merged['sales_price']/PLAN*100)
    merged.sort_values('sales_price', ascending=False, inplace=True)
    print(merged)

    leaderboard = [{"name": i['responsible_user'], "average": simplifyNumber(round(i['sales_price']/i['sales_count'])), "sales_price": simplifyNumber(i["sales_price"]), "conversion": int(i['conversion'])} for i in merged.to_dict('records')]
    data = {
        'leaderboard': leaderboard,
        'staff': merged.to_dict('records')
    }
    return render(r, 'home.html', context=data)


def simplifyNumber(n):
    return "{:,}".format(n)

