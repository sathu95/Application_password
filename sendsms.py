from google.appengine.api import urlfetch # used to connect to 3rd party APIs
from google.appengine.api import taskqueue
import jinja2 # used for templating
import logging
import os
import urllib

SEND_SMS = True

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class SendSMS:
    def verifyPasswordAdd(self, to, id):
        id = str(id)

        template_values = {
            'id' : id,
            'action' : 'add'
        }

        template = JINJA_ENVIRONMENT.get_template('templates/verify.sms')
        text = template.render(template_values)

        self.send(to, text)
        return text

    def verifyDelete(self, to, id):
        id = str(id)

        template_values = {
            'id' : id,
            'action' : 'delete'
        }

        template = JINJA_ENVIRONMENT.get_template('templates/verify.sms')
        text = template.render(template_values)

        self.send(to, text)
        return text

    def sendPassword(self, to, password):

        template_values = {
            'password' : password
        }

        template = JINJA_ENVIRONMENT.get_template('templates/retrieve.sms')
        text = template.render(template_values)

        self.send(to, text)
        return text

    def send(self, to, text):
        taskqueue.add(url='/_workerrun', params={'to': to, 'text': text}, method="GET")

    def sendNotQueued(self, to, text):

        smsFields = {
            'api_key': '40221fd6',
            'api_secret': '8S7QUHgCanLldLF9',
            'to': to,
            'from': 'MySecret',
            'text': text
        }

        if SEND_SMS == True:
            logging.info('sending sms: ' ) # + to + " - " + text

            try:
                form_data = urllib.urlencode(smsFields)
                headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                result = urlfetch.fetch(
                    url='https://rest.nexmo.com/sms/json',
                    payload=form_data,
                    method=urlfetch.POST,
                    headers=headers)
                #logging.info(result.content)

                return True
            except urlfetch.Error:
                logging.info('failed to send sms: ' ) # + to + " - " + text
                logging.exception('Caught exception fetching url')
                return False
        else:
            logging.info('sending sms (turned off by SEND_SMS flag): ') #+ to + " - " + text