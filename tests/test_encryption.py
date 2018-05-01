#!/usr/bin/env python2

import os
import sys
sys.path.insert(0,'..') #include files from parent folder

from encrypt import Encrypt

def test_encryption():
    # Define intputs to check
    mobile = "+447740193397"
    password_input = "456"
    password_encrypted = "LfrpS0GQHWrK7Bf3hymo2lY53xZVcIxthjTG92E5s97DpBgwIq0le5CkwxS5gy/r"

    verification_id_input = "5240822173794304"
    verification_id_encrypted = "5RCQVvDLFeIkbOKUkXq4xUfLOUJbF5piAtoLRtvFKhUbtJvvO7wV9cQXhtsQj5jq"

    # Create test object
    encrypt = Encrypt()

    # Test
    print('Test that a key has been loaded')
    assert len(encrypt.key) > 10

    # Test
    print('test encryption without a salt')
    e = encrypt.encryptString(verification_id_input)
    assert verification_id_encrypted == e

    # Test
    print('test encryption with a salt')
    e = encrypt.encryptString(password_input, mobile)
    assert password_encrypted == e

    print("Success")

if __name__ == "__main__":
    test_encryption()