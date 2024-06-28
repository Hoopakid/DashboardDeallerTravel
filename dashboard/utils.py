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
    get_in_data = by_users()
    if get_in_data != {}:
        response = requests.get(API_URL + 'get-ticket-data')
        if response.status_code == 200:
            new_response = requests.get(NEW_API_URL + 'api/get-sarkor-data')
            if new_response.status_code == 200:
                call_data = new_response.json()
                sales_data = response.json()
                returning_users = []
                ctx = {call['name'].lower(): call for call in call_data['ctx']}

                users_set = set(user['name'].lower() for user in call_data['ctx']) | set(
                    sale.get('responsible_user', '').lower() for sale in sales_data)

                for user_name in users_set:
                    user_name_lower = user_name.lower()

                    if user_name_lower in ['samandar', 'dimitriy']:
                        user_name_lower = 'samandar'
                        responsible_user = 'Samandar'
                    else:
                        responsible_user = user_name.capitalize()

                    matched_user = difflib.get_close_matches(user_name_lower, get_in_data.keys(), n=1, cutoff=0.6)
                    user_data = get_in_data.get(matched_user[0]) if matched_user else {}

                    sales_info_list = [sale for sale in sales_data if
                                       sale.get('name', '').lower() in ['samandar', 'dimitriy']]

                    combined_sales_info = {
                        'today_opportunity': sum(sale.get('today_opportunity', 0) for sale in sales_info_list),
                        'today_count': sum(sale.get('today_count', 0) for sale in sales_info_list),
                        'monday': sum(sale.get('monday', 0) for sale in sales_info_list),
                        'tuesday': sum(sale.get('tuesday', 0) for sale in sales_info_list),
                        'wednesday': sum(sale.get('wednesday', 0) for sale in sales_info_list),
                        'thursday': sum(sale.get('thursday', 0) for sale in sales_info_list),
                        'friday': sum(sale.get('friday', 0) for sale in sales_info_list),
                        'saturday': sum(sale.get('saturday', 0) for sale in sales_info_list),
                        'sunday': sum(sale.get('sunday', 0) for sale in sales_info_list)
                    }

                    call_info = ctx.get(user_name_lower, {})

                    temp = {
                        'responsible_user': responsible_user,
                        'sales_price': combined_sales_info.get('today_opportunity', 0),
                        'sales_count': combined_sales_info.get('today_count', 0),
                        'call_average': call_info.get('calls_average', 0),
                        'missed_calls': call_info.get('missed_calls_count', 0),
                        'call_in': call_info.get('call_in', 0),
                        'call_out': call_info.get('call_out', 0),
                        'all_calls': call_info.get('all_calls_count', 0),
                        'call_seconds': call_info.get('calls_second', 0),
                        'all_time': user_data.get('all', ''),
                        'in_time': user_data.get('in', ''),
                        'out_time': user_data.get('out', ''),
                        'weekly': {'monday': combined_sales_info.get('monday', 0),
                                   'tuesday': combined_sales_info.get('tuesday', 0),
                                   'wednesday': combined_sales_info.get('wednesday', 0),
                                   'thursday': combined_sales_info.get('thursday', 0),
                                   'friday': combined_sales_info.get('friday', 0),
                                   'saturday': combined_sales_info.get('saturday', 0),
                                   'sunday': combined_sales_info.get('sunday', 0)}
                    }

                    returning_users.append(temp)
                conversed_users = sum_conversion(returning_users)
                filtered_data = [user for user in conversed_users if user['responsible_user'] != 0 and user[
                    'responsible_user'] != 'Отдел продажи авиакасса' and user['responsible_user'] != '' and user[
                                     'responsible_user'] != 'Дилноза мухаммадсалиевна']
                return filtered_data
            return []
        return []
    return []
