from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.shortcuts import render, redirect
from .models.forms import RegistrationForm
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.http import Http404
from django.contrib import messages
import sweetify
from kryptonite.dataservice.binance_.binance_client import BinanceClient
from kryptonite.dataservice.poloniex.client import PoloniexClient
from datetime import datetime
from .userservice.user_service import *

import logging

logger = logging.getLogger(__name__)


def index(request):
    if request.user.is_authenticated:
        fav_exchange_values = [vars(exch) for exch in get_favourite_exchanges(request.user.id)]
        exch_dict = {}
        for exch in fav_exchange_values:
            del exch['_state']
            exch_dict[exch['value']] = exch
        fav_currency_values = [vars(curr) for curr in get_favourite_currencies(request.user.id)]
        for curr in fav_currency_values:
            del curr['_state']
        show_charts = exch_dict and fav_currency_values
        return render(request, 'user_index.html',
                      {'exchanges': exch_dict, 'currencies': fav_currency_values, 'show_charts': show_charts})
    else:
        exchanges = [vars(exch) for exch in get_all_exchanges()]
        exch_dict = {}
        for exch in exchanges:
            del exch['_state']
            exch_dict[exch['value']] = exch
        currencies = [vars(curr) for curr in get_all_currencies()]
        for curr in currencies:
            del curr['_state']
        return render(request, 'index.html', {'exchanges': exch_dict, 'currencies': currencies})


def all_data_page(request):
    exchanges = [vars(exch) for exch in get_all_exchanges()]
    exch_dict = {}
    for exch in exchanges:
        del exch['_state']
        exch_dict[exch['value']] = exch
    currencies = [vars(curr) for curr in get_all_currencies()]
    for curr in currencies:
        del curr['_state']
    return render(request, 'index.html', {'exchanges': exch_dict, 'currencies': currencies})


def get_historical_binance_data(request):
    client = BinanceClient()
    symbol = request.GET['symbol']
    interval = request.GET['interval']
    date_start = datetime.strptime(request.GET['date_start'], "%a, %d %b %Y %H:%M:%S %Z")
    data = client.get_historical_data_with_interval(symbol, interval, date_start)
    li = [{"open_time": record[0], "open": record[1]} for record in data]
    return JsonResponse(li, safe=False)


def get_historical_poloniex_data(request):
    client = PoloniexClient()
    symbol = request.GET['symbol']
    interval = _map_intervals(request.GET['interval'])
    date_start = datetime.strptime(request.GET['date_start'], "%a, %d %b %Y %H:%M:%S %Z")
    date_start = _timestamp_gmt_to_utc(date_start.timestamp())
    date_end = datetime.now().timestamp()
    data = client.get_chart_data(symbol, int(date_start), int(date_end), interval)
    li = [{"open_time": record.date, "open": record.open} for record in data]
    return JsonResponse(li, safe=False)


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            if user is not None:
                sweetify.success(request, title='Success', icon='success', text='Registration successful',
                                 timer=5000, button='Ok')
                login(request, user)
                return redirect('/')
            else:
                return render(request, 'register.html', {'form': form})

    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                sweetify.success(request, title='Success', icon='success', text='Login successful',
                                 timer=5000, button='Ok')
                return redirect('/')
            else:
                return render(request, 'login.html', {'form': form})
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


@login_required
def logout_user(request):
    logout(request)
    sweetify.success(request, title='Success', icon='success', text='You have been logged out',
                     timer=5000, button='Ok')
    return redirect('/')


@login_required
def favourites(request):
    all_currencies = get_all_currencies()
    fav_currencies = get_favourite_currencies(request.user.id)
    rest_currencies = list(set(all_currencies) - set(fav_currencies))

    all_exchanges = get_all_exchanges()
    fav_exchange = get_favourite_exchanges(request.user.id)
    rest_exchange = list(set(all_exchanges) - set(fav_exchange))
    return render(request, 'favourites.html',
                  {'currencies': rest_currencies,
                   'curr_buttons': fav_currencies,
                   "exchange_buttons": fav_exchange,
                   "exchanges": rest_exchange})


@login_required
def del_favourite_currency(request):
    if not request.is_ajax():
        raise Http404
    else:
        curr_id = request.POST.get("id", None)
        FavouriteCurrency.objects.filter(user_id=request.user.id, currency_id=curr_id).delete()
        return JsonResponse({"id": curr_id})


@login_required
def add_favourite_currency(request):
    if not request.is_ajax():
        raise Http404
    else:
        curr_id = request.POST.get("id", None)
        fav = FavouriteCurrency(user_id=request.user.id, currency_id=curr_id)
        fav.save()
        return JsonResponse({"id": curr_id})


@login_required
def del_favourite_exchange(request):
    if not request.is_ajax():
        raise Http404
    else:
        exch_id = request.POST.get("id", None)
        FavouriteExchange.objects.filter(user_id=request.user.id, exchange_id=exch_id).delete()
        return JsonResponse({"id": exch_id})


@login_required
def add_favourite_exchange(request):
    if not request.is_ajax():
        raise Http404
    else:
        exch_id = request.POST.get("id", None)
        fav = FavouriteExchange(user_id=request.user.id, exchange_id=exch_id)
        fav.save()
        return JsonResponse({"id": exch_id})


@login_required
def account(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            sweetify.success(request, title='Success', icon='success', text='You successfully changed your password',
                             timer=5000, button='Ok')
            return redirect('account')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'account.html', {
        'form': form
    })


@login_required
def arbitrage(request):
    # TODO
    return render(request, 'arbitrage.html')


def _timestamp_gmt_to_utc(timestamp):
    return timestamp + 7200


def _map_intervals(interval):
    if interval == '5m':
        return 300
    if interval == '1h':
        return 1800
    if interval in ['1d', '1y']:
        return 86400
