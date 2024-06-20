import os, pandas as pd, requests
from datetime import datetime
from pprint import pprint
from django.shortcuts import render
from fuzzywuzzy import process, fuzz

from .utils import find_best_match, normalize_name, remove_numbers, transliterate_name, get_token, get_amocrm_leads

# Create your views here.
def home(r):
    today = datetime.now()
    start_date_unix = int(today.replace(hour=0, minute=0, second=0).timestamp())
    end_date_unix = int(today.replace(hour=23, minute=59, second=59).timestamp())

    crm_data = get_amocrm_leads(os.environ.get('AMOCRM_TOKEN'), os.environ.get('AMOCRM_URL'), start_date_unix, end_date_unix, 'updated_at')
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

    panel_data['sales_count'] = panel_data['sales_count'].str.replace(r'[^\d]', '', regex=True).astype(int)
    panel_data['sales_price'] = panel_data['sales_price'].str.replace(r'[^\d]', '', regex=True).astype(int)
    panel_data['name'] = panel_data['name'].apply(lambda x: normalize_name(x))
    
    # panel_data = {normalize_name(k): v for k, v in panel_data.items()}


    by_staff_leads = crm_data.groupby('responsible_user').aggregate(
        leads=('id', 'count'),
    ).reset_index()
    print(by_staff_leads)
    crm_names = crm_data['responsible_user'].unique()
    panel_data['matched_name'] = panel_data['name'].apply(find_best_match, args=(crm_names,))
    print(panel_data)



    # Map and update names in the panel data to match CRM names
    # mapped_panel_data = []
    # for entry in panel_data:
    #     panel_name = list(entry.keys())[0]
    #     matched_name = find_best_match(panel_name, crm_names)
    #     if matched_name:
    #         original_name = crm_data[crm_data['normalized_name'] == matched_name]['responsible_user'].values[0]
    #         mapped_panel_data.append({original_name: entry[panel_name]})
    #     else:
    #         mapped_panel_data.append({panel_name: entry[panel_name]})  # Keep original if no match

    # print(mapped_panel_data)

    data = {
        # 'leaderboard': leaderboard
    }
    return render(r, 'home.html', context=data)


def simplifyNumber(n):
    return "{:,}".format(n)

