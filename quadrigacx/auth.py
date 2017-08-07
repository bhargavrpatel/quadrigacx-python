# coding: utf-8
import hashlib
import hmac
import time

from requests.auth import AuthBase


class HMACAuth(AuthBase):
    """HMAC Auth.

    An `AuthBase` implementation to handle authenticated calls to Quadriga CX.

    When an instance of `HAMCAuth` is passed a `request.Request` object, it
    updates the respective headers by adding `key`, `nonce`, and `signature`
    params.

    Parameters
    ----------
    api_key: str
    api_secret: str
    client_id: int or str

    """

    def __init__(self, api_key, api_secret, client_id):
        self.key = api_key
        self.id = str(client_id)
        self.secret = api_secret

    def __call__(self, request):
        nonce = int(time.time())
        hmac_key = str(nonce) + self.id + self.key
        signature = hmac.new(self.secret.encode(), hmac_key, hashlib.sha256)
        request.headers.update({
            'key': self.key,
            'nonce': nonce,
            'signature': signature.hexdigest()
        })
        return request
