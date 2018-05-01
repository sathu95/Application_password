#!/usr/bin/env python

import jinja2 # used for templating
import webapp2 # used for routing of web requests
import logging
import os
import urllib
from datetime import datetime, timedelta
import random

# Google App Engine Imports
from google.appengine.ext import ndb # used to store data in Google's Datastore
from google.appengine.api import taskqueue
from google.appengine.api import app_identity

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

from encrypt import Encrypt
from sendsms import SendSMS

# Define Object Relational Mappings
# These define the data types that are being stored
class PasswordStore(ndb.Model):
    mobileNumber = ndb.StringProperty(indexed=True)
    clue = ndb.StringProperty(indexed=True)
    encryptedPassword = ndb.StringProperty(indexed=False)
    created = ndb.DateTimeProperty(auto_now_add=True)
    confirmed = ndb.IntegerProperty(indexed=True)

class Verification(ndb.Model):
    passwordStoreId = ndb.IntegerProperty(indexed=True)
    action = ndb.StringProperty(indexed=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    confirmed = ndb.IntegerProperty(indexed=True)

class RateManager(ndb.Model):
    mobileNumber = ndb.StringProperty(indexed=True)
    created = ndb.DateTimeProperty(auto_now_add=True)

# Handle adding of password
class PasswordAdd(webapp2.RequestHandler):
    def get(self):
        template_values = {
            'nav' : 'store'
        }

        template = JINJA_ENVIRONMENT.get_template('templates/store.html')
        self.response.write(template.render(template_values))

    def post(self):
        # Step 1 - retrieve and verify user input
        clue = self.request.get('clue').strip()
        mobileNumber = "+44" + self.request.get('mobilenumber').strip()
        password = self.request.get('pass').strip()

        # Step 2 - store the password
        encrypt = Encrypt()
        e = encrypt.encryptString(password, mobileNumber)

        passwordStorerecord = PasswordStore()
        passwordStorerecord.clue = clue
        passwordStorerecord.mobileNumber = mobileNumber
        passwordStorerecord.encryptedPassword = e
        passwordStorerecord.confirmed = 0
        passwordStorerecord.put()

        passwordStoreId = passwordStorerecord.key.id() # the id of the record just created
        logging.info('storing password id: ' + str(passwordStoreId))

        # Step 3 - store verification record
        verificationRecord = Verification()
        verificationRecord.action = 'add'
        verificationRecord.confirmed = 0
        verificationRecord.passwordStoreId = passwordStoreId
        verificationRecord.put()

        verificationRecordId = verificationRecord.key.id() # the id of the record just created
        logging.info('storing verification id: ' + str(verificationRecordId))

        # Step 4 - send SMS with encrypted verification
        i = str(verificationRecordId)
        e = encrypt.encryptString(i)
        d = encrypt.decryptString(e)

        sms = SendSMS()
        sms.verifyPasswordAdd(mobileNumber, e)

        logging.info('sending verification: ' + " - " + i + " - " + e + " - " + d)

        # Step 5 - render reply

        template_values = {
            'nav' : 'store',
            'id' : e
        }

        template = JINJA_ENVIRONMENT.get_template('templates/check_phone_success.html')
        self.response.write(template.render(template_values))

# Handle Retrieval of passwords
class PasswordRetrieve(webapp2.RequestHandler):
    def get(self):
        template_values = {
            'nav' : 'retrieve',
            'function' : 'PasswordRetrieve get' #urllib.quote_plus(guestbook_name),
        }

        template = JINJA_ENVIRONMENT.get_template('templates/retrieve.html')
        self.response.write(template.render(template_values))

    def post(self):
        clue = self.request.get('clue')
        mobileNumber =  "+44" + self.request.get('mobilenumber')

        query = PasswordStore.query(ndb.AND(PasswordStore.clue == clue, PasswordStore.mobileNumber == mobileNumber, PasswordStore.confirmed == 1)).order(-PasswordStore.created)
        result = query.fetch(1)

        if result:
            encrypt = Encrypt()

            #logging.info('found: ' + clue + " - " + mobileNumber)
            sms = SendSMS()
            sms.sendPassword(mobileNumber, encrypt.decryptString(result[0].encryptedPassword, mobileNumber))
        #else:
            #logging.info('not found: ' + clue + " - " + mobileNumber)

        template_values = {
            'nav': 'retrieve'
        }

        template = JINJA_ENVIRONMENT.get_template('templates/success.html')
        self.response.write(template.render(template_values))

# Handle deleting of passwords
class PasswordDelete(webapp2.RequestHandler):
    def get(self):
        template_values = {
            'nav' : 'delete'
        }

        template = JINJA_ENVIRONMENT.get_template('templates/delete.html')
        self.response.write(template.render(template_values))

    def post(self):
        # Step 1 - retrieve and verify user input
        clue = self.request.get('clue').strip()
        mobileNumber = "+44" + self.request.get('mobilenumber').strip()

        # Step 2 - get the password record

        query = PasswordStore.query(ndb.AND(PasswordStore.clue == clue, PasswordStore.mobileNumber == mobileNumber)).order(-PasswordStore.created)
        passwordStorerecord = query.fetch(1)

        if passwordStorerecord:
            #logging.info('found: ' + clue + " - " + mobileNumber)

            passwordStorerecord = passwordStorerecord[0]
            passwordStoreId = passwordStorerecord.key.id()  # the id of the record just created

            # Step 3 - store verification record
            verificationRecord = Verification()
            verificationRecord.action = 'delete'
            verificationRecord.confirmed = 0
            verificationRecord.passwordStoreId = passwordStoreId
            verificationRecord.put()

            verificationRecordId = verificationRecord.key.id()  # the id of the record just created
            logging.info('storing verification id: ' + str(verificationRecordId))

            # Step 4 - send SMS with encrypted verification

            encrypt = Encrypt()

            i = str(verificationRecordId)
            e = encrypt.encryptString(i)
            d = encrypt.decryptString(e)

            sms = SendSMS()
            sms.verifyDelete(mobileNumber, e)

            logging.info('sending delete verification: ' + " - " + i + " - " + e + " - " + d)
        #else:
            #logging.info('not found: ' + clue + " - " + mobileNumber)

        # Step 5 - render reply
        template_values = {
            'nav': 'delete',
            'id': e
        }

        template = JINJA_ENVIRONMENT.get_template('templates/check_phone_success.html')
        self.response.write(template.render(template_values))

# Handle help request
class Help(webapp2.RequestHandler):

    def get(self):
        template_values = {
            'nav' : 'help'
        }

        template = JINJA_ENVIRONMENT.get_template('templates/help.html')
        self.response.write(template.render(template_values))

# Handle verification requests
class Verify(webapp2.RequestHandler):
    def get(self):

        template = 'error.html'
        template_values = {
            'nav': 'none'
        }

        if (self.request.get('id')):
            encrypt = Encrypt()
            verificationId = int(encrypt.decryptString(self.request.get('id')))

            verificationRecord = Verification.get_by_id(verificationId)
            logging.info(verificationRecord)


            if verificationRecord:
                passwordStorerecord = PasswordStore.get_by_id(verificationRecord.passwordStoreId)

                if passwordStorerecord:
                    # Handle the add verification step
                    if verificationRecord.action == 'add':
                            passwordStorerecord.confirmed = 1
                            passwordStorerecord.put()
                            verificationRecord.key.delete()
                            logging.info('Updated records - verification (deleted) and passwordStore (updated)')
                            template = 'success.html'

                    # Handle the delete verification step
                    if verificationRecord.action == 'delete':
                            passwordStorerecord.key.delete()
                            verificationRecord.key.delete()
                            logging.info('Updated records - verification (deleted) and passwordStore (deleted)')
                            template = 'success.html'
                    else:
                        logging.info(
                            'Failed to retrieve Verification record id: ' + str(verificationId))
                else:
                    logging.info('Failed to retrieve PasswordStore record id: ' + str(verificationRecord.passwordStoreId))
            else:
                template = 'error.html'

        template = JINJA_ENVIRONMENT.get_template('templates/' + template)
        self.response.write(template.render(template_values))

    def post(self):
        template = JINJA_ENVIRONMENT.get_template('templates/error.html')
        self.response.write(template.render())

# Handles clean up CRON job - ensures that only GAE can call the function
class CleanUp(webapp2.RequestHandler):
    def get(self):
        if not ("X-Appengine-Cron" in self.request.headers):
            # ensure that the cleanup method is only called by GAE
            logging.warning("Cron being called NOT by GAE")
            template = JINJA_ENVIRONMENT.get_template('templates/404.html')
            self.response.set_status(404)
            self.response.write(template.render())
            return

        logging.info("Clean Up cron running")

        query = PasswordStore.query(ndb.AND(PasswordStore.created < datetime.now() - timedelta(days=2), PasswordStore.confirmed == 0)).order(-PasswordStore.created)
        result = query.fetch()


        self.response.write(result)

        for i in result:
            i.key.delete()

        query = Verification.query(ndb.AND(Verification.created < datetime.now() - timedelta(days=2)))
        result = query.fetch()

        for i in result:
            i.key.delete()

        self.response.write(result)

    def test(self):
        logging.info("test url")
        self.response.write('test create')

# Handles clean up test functionality - only available on DEV
class CleanUpTest(webapp2.RequestHandler):
    def get(self):
        if isDev(self.request.host):
            logging.info("creating test password records")
            for i in xrange(1, 11):
                created = datetime.now() - timedelta(days=i)

                mobileNumber = "+" + str(447700000000 + i)
                clue = "clue" + str(i)
                password = "password" + str(i)
                encrypt = Encrypt()
                e = encrypt.encryptString(password, mobileNumber)

                passwordStorerecord = PasswordStore()
                passwordStorerecord.clue = clue
                passwordStorerecord.mobileNumber = mobileNumber
                passwordStorerecord.encryptedPassword = e
                passwordStorerecord.confirmed = random.choice([0, 1])
                passwordStorerecord.created = created
                passwordStorerecord.put()

            logging.info("creating test verification records")
            for i in xrange(1, 11):
                created = datetime.now() - timedelta(days=i)
                verificationRecord = Verification()

                verificationRecord.action = random.choice(['delete', 'add'])
                verificationRecord.confirmed = random.choice([0, 1])
                verificationRecord.passwordStoreId = 1000 + i * 17
                verificationRecord.created = created
                verificationRecord.put()

            self.response.write("done")

        logging.warning("Tried to activate CleanUpTest not in dev")

# Handles creation of test worker - only available on DEV
class WorkerQueue(webapp2.RequestHandler):
    def get(self):
        if isDev(self.request.host):
            sms = SendSMS()
            sms.send('+447740193397', 'test queue')

            self.response.write("done")

        logging.warning("Tried to activate WorkerQueue not in dev")

def CheckRate(mobileNumber):
    logging.info("Checking rate for: " + mobileNumber)
    last24hours = datetime.now() - timedelta(days=1)

    query = RateManager.query(ndb.AND(RateManager.created > last24hours, RateManager.mobileNumber == mobileNumber))
    resultCount = query.count()
    if (resultCount < 40):
        rate = RateManager()
        rate.mobileNumber = mobileNumber
        rate.put
        logging.info("Rate is fine for:" + mobileNumber)
        return True

        logging.info("Rate exceeded for:" + mobileNumber)
    return False

# Handle worker threads - ensures that only GAE can call the function
class WorkerRun(webapp2.RequestHandler):
    def get(self):
        if not ("X-Appengine-Queuename" in self.request.headers):
            logging.warning("worker activated not in GAE")
            template = JINJA_ENVIRONMENT.get_template('templates/404.html')
            self.response.set_status(404)
            self.response.write(template.render())
            return

        # if running in GAE send text
        to = self.request.get('to')
        text = self.request.get('text')

        logging.info("worker activated")

        if CheckRate(to):
            sms = SendSMS()
            sms.sendNotQueued(to, text)

def isDev(host):
    return "172.29.255.244" in host

app = webapp2.WSGIApplication([
    ('/', PasswordAdd),
    ('/passwordadd', PasswordAdd),
    ('/passwordretrieve', PasswordRetrieve),
    ('/passworddelete', PasswordDelete),
    ('/help', Help),
    ('/verify', Verify),
    ('/_cleanup', CleanUp), # GAE internal function
    ('/_workerrun', WorkerRun), # GAE internal function
    ('/dev_cleanuptest', CleanUpTest), # dev function
    ('/dev_workerqueue', WorkerQueue) # dev function
], debug=False)

def handle_404(request, response, exception):
    logging.exception(exception)
    template = JINJA_ENVIRONMENT.get_template('templates/404.html')
    response.write(template.render())
    response.set_status(404)

def handle_500(request, response, exception):
    logging.exception(exception)
    template = JINJA_ENVIRONMENT.get_template('templates/500.html')
    response.write(template.render())
    response.set_status(500)

app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500
