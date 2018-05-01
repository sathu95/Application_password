#!/usr/bin/env python
import uuid
import os
import requests

BASE_URL = 'http://localhost:8080'


def test_e2e():
    assert BASE_URL

    testUrls = []
    testUrls.append({'url': '/', 'test': 'Punch & Store'})
    testUrls.append({'url': '/passwordadd', 'test': 'Punch & Store'})
    testUrls.append({'url': '/passwordretrieve', 'test': 'My password is?'})
    testUrls.append({'url': '/passworddelete', 'test': 'Wipe it out'})
    testUrls.append({'url': '/help', 'test': 'Terms and Conditions'})
    testUrls.append({'url': '/verify', 'test': 'Something went wrong :-('})
    testUrls.append({'url': '/DOESNOTEXIST', 'test': "What you search for cannot be found"})

    for test in testUrls:
        url = BASE_URL + test["url"]
        print("\nTesting: " + url)
        r = requests.get(url)

        print("Checking length of content is greater than 1024")
        assert len(r.content) > 1024
        print("Checking for opening HTML tag")
        assert "<html>" in r.content
        print("Checking for closing HTML tag")
        assert "</html>" in r.content
        print("Checking test content is present")
        assert test["test"] in r.content

    print("Success")

if __name__ == "__main__":
    test_e2e()
