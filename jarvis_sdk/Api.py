"""
Copyright (c) 2021 Philipp Scheer
"""


import requests


class Api():
    BASE_URL = "http://api.jarvis.fipsi.at"

    @staticmethod
    def endpoint(endpoint, post_data={}):
        """Call an endpoint of the official Jarvis API"""
        return Api.post(f"{Api.BASE_URL}{endpoint}", post_data=post_data)

    @staticmethod
    def post(url, post_data={}):
        """Perform a HTTP POST request to given `url` with given `post_data`"""
        return requests.post(url, json=post_data).json()
    
    @staticmethod
    def get(url):
        """Perform a HTTP GET request to given `url`"""
        return requests.get(url).json()
