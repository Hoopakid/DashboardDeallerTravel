from django.shortcuts import render
from .utils import get_deals


def home(r):
    data = get_deals()
    informations = {'leaderboard': data}
    return render(r, 'home.html', context=informations)

