import os
import requests
from django.shortcuts import render
from .utils import get_datas


def home(r):
    users_data = get_datas()
    informations = {
        'leaderboard': users_data
    }
    return render(r, 'home.html', context=informations)
