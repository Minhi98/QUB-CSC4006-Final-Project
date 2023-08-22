# adds higher directory to python modules path
import sys
sys.path.append("..")

from var import *
from utilities import *


"""
Unit tests for the integration microservice, grouping tests by python module.

Certain functions like utilities.validate_arg_email() are exempted as they are
mostly the function of a third-party module with a minor addition 
(in this example validate_arg_email just wraps the function in an exception handler)
"""

class TestVarUtils:
    service = {
        "URL": "test.example.com",
        "HTTPS": True
    }

    def test_url(self):
        res = URL(self.service)
        assert res == "https://test.example.com"

    def test_datastore_url(self):
        res = DatastoreURL(self.service)
        assert res == "https://test.example.com/data"

class TestUtilities:
    secret_key = "test"
    jwt_datastore = {
        1: {"ID": 12, "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2Nzk1MDI2NTksImlhdCI6MTY3OTQxNjI1OSwic3ViIjoidGVzdDEyM0BlbWFpbC5jb20ifQ.KSvsEsE-zjZ70p-N0aHjYW0O5nvz98y2ApLrh3R9h9M", "blacklisted": "0"},
        2: {"ID": 13, "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2Nzk1MDY1ODgsImlhdCI6MTY3OTQyMDE4OCwic3ViIjoidGVzdDEyM0BlbWFpbC5jb20ifQ.P3wBzC93uh6DftcVnZI4AOYULOMH_C-3FIj8HXAfFJ0", "blacklisted": "0"},
        3: {"ID": 14, "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2Nzk1MjY1NDksImlhdCI6MTY3OTQ0MDE0OSwic3ViIjoidGVzdDEyM0BlbWFpbC5jb20ifQ.Ch74ZfVXP-NexJrdLyMbVgIAEqEjdPzDH4gtrUXsvuA", "blacklisted": "1"},
    }

    # tests get_from_datastore by using jwt_datastore as an example of correctly fetched data

    def test_get_from_datastore_local(self):
        assert filter_from_datastore(self.jwt_datastore) == self.jwt_datastore

    def test_get_from_datastore_local_search_only(self):
        rows = self.jwt_datastore
        search_filter = ("ID", 12)
        assert filter_from_datastore(rows, search_filter=search_filter) == {1: self.jwt_datastore[1]}

    def test_get_from_datastore_local_search_with_partial(self):
        rows = self.jwt_datastore
        search_filter = ("token", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")
        assert filter_from_datastore(rows, search_filter=search_filter, partial_match=True) == self.jwt_datastore

    def test_get_from_datastore_local_search_with_unique(self):
        rows = self.jwt_datastore
        search_filter = ("blacklisted", "1")
        assert filter_from_datastore(rows, search_filter=search_filter, unique_match=True) == {3: self.jwt_datastore[3]} 

