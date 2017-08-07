# coding: utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import hashlib
import hmac
import requests
import time
import warnings

from quadrigacx.currencies import OrderBook
from quadrigacx.currencies import FiatCurrencies
from quadrigacx.utils import imap
from quadrigacx.utils import quote
from quadrigacx.utils import urljoin


def login_required(func):
    """Auth Required.

    Used to ensure calls to private methods do not occur without authentication.
    Note that this is simply a way to handle bad calls prior to sending a
    request to Quadriga server. If the user is not authenticated, the request
    will fail anyway.

    """
    def _call(*args, **kwargs):
        # Ensure the client is authenticated
        client = args[0]
        assert isinstance(client, Client)
        assert client._authenticated
        return func(*args, **kwargs)
    return _call


class Client(object):
    """ API Client for the Quadriga Coin Exchange v2 API.

    A simple wraper around the v2 API of Quadriga Coin Exchange.

    """

    BASE_URI = 'https://api.quadrigacx.com/v2/'

    def __init__(self, api_key=None, api_secret=None, client_id=None):
        if api_key and not api_secret:
            ValueError('Missing `api_secret`')
        elif not api_key and api_secret:
            ValueError('Missing `api_key`.')

        self.key = api_key if api_key else None
        self.id = client_id if client_id else str(1)
        self.secret = api_secret.encode() if api_secret else None
        self._authenticated = (False if not self.key and
                               not self.secret else True)
        self._session = self._session_builder()

    @property
    def authenticated(self):
        """Denotes the type of the client."""
        return self._authenticated

    @property
    def session(self):
        """Client Request session instance."""
        if not hasattr(self, '_session'):
            # Only allow for non-authenticated session this way.
            self._session = self._session_builder()

        return self._session

    def _session_builder(self):
        """Session Builder.

        Creates a Request Session. If Authbase is provided, sets up
        authentication for private calls

        """
        session = requests.session()
        session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'quadrigacx-python/v2.0'
        })
        return session

    def _build_url(self, *parts):
        '''Build url'''
        return urljoin(self.BASE_URI, '/'.join(imap(quote, parts)))

    def _sign(self, data):
        nonce = int(time.time())
        hmac_key = str(nonce) + self.id + self.key
        signature = hmac.new(self.secret, hmac_key, hashlib.sha256)
        data.update({
            'key': self.key,
            'nonce': nonce,
            'signature': signature.hexdigest()
        })
        return data

    # Public Functions
    def get_ticker(self, order_book=None):
        """Get current Ticker Information.

        Implements: `GET https://api.quadrigacx.com/v2/ticker?book=XXX`

        Parameters
        ----------
        order_book: None or quadrigacx.currencies.OrderBook (Default: None)
            An Enum of the supported order books. If no order_book is given,
            it defaults to `quadrigacx.currencies.OrderBook.canadian_bitcoin`.

        """
        if order_book is not None and not isinstance(order_book, OrderBook):
            raise ValueError('order_book must be an instance of '
                             '`quadrigacx.currencies.OrderBook`.')
        url = self._build_url('ticker')
        book = order_book if order_book else OrderBook.canadian_bitcoin
        response = self.session.get(url, params={
            'book': book.value
        })
        return response


    def get_order_book(self, order_book=None, group_by_price=True):
        """Lists all Open Orders.

        Implements: `GET https://api.quadrigacx.com/v2/order_book`

        Parameters
        ---------
        order_book: None or quadrigacx.currencies.OrderBook (Default: None)
            An Enum of the supported order books. If no order_book is given,
            it defaults to `quadrigacx.currencies.OrderBook.canadian_bitcoin`.
        group_by_price: bool (Default: True)
            Groups order by same price.

        """
        if order_book is not None and not isinstance(order_book, OrderBook):
            raise ValueError('order_book must be an instance of '
                             '`quadrigacx.currencies.OrderBook`.')
        url = self._build_url('order_book')
        group = 1 if group_by_price else 0
        book = order_book if order_book else OrderBook.canadian_bitcoin
        response = self.session.get(url, params={
            'book': book.value,
            'group': group
        })
        return response.json()


    def get_transactions(self, order_book=None, timeframe='minute'):
        """Get transactions.

        Implements: `GET https://api.quadrigacx.com/v2/transactions`

        Retrieves transactions for a given book within a time frame.

        Parameters
        ----------
        order_book: None or quadrigacx.currencies.OrderBook (Default: None)
            An Enum of the supported order books. If no order_book is given,
            it defaults to `quadrigacx.currencies.OrderBook.canadian_bitcoin`.
        timeframe: str
            A window within which all of the transactions are to be fetched.
            Can be either `minute` or `hour`.

        """
        if timeframe not in {'minute', 'hour'}:
            raise ValueError('timeframe must be one of `minute` or `hour`')
        if order_book is not None and not isinstance(order_book, OrderBook):
            raise ValueError('order_book must be an instance of '
                             '`quadrigacx.currencies.OrderBook`.')
        url = self._build_url('transactions')
        book = order_book if order_book else OrderBook.canadian_bitcoin
        response = self.session.get(url, params={
            'book': book.value,
            'minute': timeframe
        })
        return response.json()

    # Private functions (Require auth)
    @login_required
    def get_balance(self):
        """Get Balance.

        Returns your current balance.
        Implements: `POST https://api.quadrigacx.com/v2/balance`

        """
        url = self._build_url('balance')
        data = self._sign({})
        import pdb; pdb.set_trace()
        response = self.session.post(url, json=data)
        return response.json()

    @login_required
    def get_user_transactions(self, offset=0, limit=50, desc=True,
                              order_book=None):
        """Get User Transactions.

        Returns all transactions performed by the authenticated account.
        Implements: `POST https://api.quadrigacx.com/v2/user_transactions`

        """
        if order_book is not None and not isinstance(order_book, OrderBook):
            raise ValueError('order_book must be an instance of '
                             '`quadrigacx.currencies.OrderBook`.')
        sort_by = 'desc' if desc else 'asc'
        url = self._build_url('user_transactions')
        book = order_book if order_book else OrderBook.canadian_bitcoin
        data = self._sign({
            'offset': offset,
            'limit': limit,
            'sort': sort_by,
            'book': book.value
        })
        response = self.session.post(url, json=data)
        return response.json()
