import os
import requests
from dotenv import load_dotenv
import difflib

from dashboard.workly_api import by_users

load_dotenv()

API_URL = os.environ.get('API_URL')
NEW_API_URL = os.environ.get('NEW_API_URL')


def sum_conversion(datas):
    for data in datas:
        data.update({
            'average_salary': round(data['sales_price'] / data['sales_count'] if data['sales_count'] != 0 else 0, 1),
            'conversion': round((data['sales_count'] / data['all_calls']) * 100 if data['all_calls'] != 0 else 0, 1)
        })
    return datas


def get_datas():
    response = requests.get(API_URL + 'get-ticket-data')
    get_in_data = by_users()
    if response.status_code == 200:
        new_response = requests.get(NEW_API_URL + 'api/get-sarkor-data')
        if new_response.status_code == 200:
            call_data = new_response.json()
            sales_data = response.json()
            returning_users = []

            if len(sales_data) >= 1 and len(call_data['ctx']) >= 1:
                ctx = {call['name'].lower(): call for call in call_data['ctx']}

                for sale in sales_data[1:]:
                    user_name = sale.get('responsible_user', '').lower()
                    best_match = difflib.get_close_matches(user_name, get_in_data.keys(), n=1, cutoff=0.6)
                    if best_match:
                        matched_user = best_match[0]
                        user_data = get_in_data[matched_user]

                        temp = {
                            'responsible_user': sale.get('responsible_user', '').capitalize(),
                            'sales_price': sale.get('opportunity', 0),
                            'sales_count': sale.get('count', 0),
                            'call_average': 0,
                            'missed_calls': 0,
                            'call_in': 0,
                            'call_out': 0,
                            'all_calls': 0,
                            'call_seconds': 0,
                            'all_time': user_data.get('all', ''),
                            'in_time': user_data.get('in', ''),
                            'out_time': user_data.get('out', '')
                        }

                        if user_name in ctx:
                            call_info = ctx[user_name]
                            temp.update({
                                'call_average': call_info.get('calls_average', 0),
                                'missed_calls': call_info.get('missed_calls_count', 0),
                                'call_in': call_info.get('call_in', 0),
                                'call_out': call_info.get('call_out', 0),
                                'all_calls': call_info.get('all_calls_count', 0),
                                'call_seconds': call_info.get('calls_second', 0)
                            })
                        elif user_name == 'dimitriy' and 'samandar1' in ctx:
                            call_info = ctx['samandar1']
                            temp.update({
                                'responsible_user': 'Samandar',
                                'call_average': call_info.get('calls_average', 0),
                                'missed_calls': call_info.get('missed_calls_count', 0),
                                'call_in': call_info.get('call_in', 0),
                                'call_out': call_info.get('call_out', 0),
                                'all_calls': call_info.get('all_calls_count', 0),
                                'call_seconds': call_info.get('calls_second', 0)
                            })

                        returning_users.append(temp)

            return sum_conversion(returning_users)
        return ''
    return ''
