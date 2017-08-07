# coding: utf-8
from enum import Enum


class FiatCurrencies(Enum):
    canadian = 'cad'
    american = 'usd'
    bitcoin = 'btc'
    ether = 'eth'


class OrderBook(Enum):
    canadian_bitcoin = 'btc_cad'
    american_bitcoin = 'btc_usd'
    ether_bitcoin = 'eth_btc'
    canadian_ether = 'eth_cad'