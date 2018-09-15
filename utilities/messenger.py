import twitter_config
import email_config

import requests
import requests_oauthlib
import time
import logging
import smtplib

##############################################################
### MessageClient
##############################################################

class Messenger:

    recipients_cache = {}

    def send_twitter_api_msg(self, message):
        logging.debug("Sending twitter_api message: %s", message)

        access_token = twitter_config.twitter_auth.get("access_token","")
        access_token_secret = twitter_config.twitter_auth.get("access_token_secret","")
        consumer_key = twitter_config.twitter_auth.get("consumer_key","")
        consumer_secret = twitter_config.twitter_auth.get("consumer_secret","")

        auth = requests_oauthlib.OAuth1(
                consumer_key,
                consumer_secret,
                access_token,
                access_token_secret)

        recipients = twitter_config.twitter_recipients
        
        recipientsList = recipients.split(",")

        # Remove empty strings
        recipientsList = filter(lambda x: len(x)>0, recipientsList) 

        for recipient in recipientsList:
            recipient_id = self.recipients_cache.get(recipient, None)
            if recipient_id == None:
                logging.debug("Looking up twitter user %s", recipient)	
                with requests.Session() as session:
                    session.auth = auth
                    try:
                        r = session.request(
                            "GET",
                            "https://api.twitter.com/1.1/users/show.json?screen_name="+recipient
                        )
                        data = r.json()
                        recipient_id = data['id_str']
                        # Cache the recipient ID for further messages
                        self.recipients_cache[recipient] = recipient_id
                    except:
                        logging.debug("Error looking up twitter user %s", recipient)
                        recipient_id = None	

            if recipient_id != None:
                logging.debug("Sending twitter api message to : %s", recipient)	
                with requests.Session() as session:
                    session.auth = auth
                    try:
                        r = session.request(
                            "POST",
                            "https://api.twitter.com/1.1/direct_messages/events/new.json",
                            json={'event': {'type': 'message_create', 'message_create': {'target': {'recipient_id': recipient_id}, 'message_data': {'text': message}}}}
                            )
                    except:
                        logging.debug("Error sending twitter api message to recipient ID ", recipient_id)


    def send_email(cEmailConfig, subject, message):
        logging.debug("Sending email message.")

        host = email_config.email_auth.get("host","")
        port = email_config.email_auth.get("port","")
        username = email_config.email_auth.get("username","")
        password = email_config.email_auth.get("password","")

        sender = email_config.email_sender
        recipients = email_config.email_recipients

        recipients_list = recipients.split(",")
        # Remove empty strings
        recipients_list = filter(lambda x: len(x)>0, recipients_list) 

        server = smtplib.SMTP_SSL(host, int(port))
        server.set_debuglevel(1)
        server.login(username, password)
        body = '\r\n'.join(['Subject: %s' % subject,
                            '', message])
        server.sendmail(from_addr=sender, to_addrs=recipients_list, msg=body)
        server.quit()


##############################################################
### UNIT TESTS (uncomment as necessary)
##############################################################

if __name__ == "__main__":

    # Test Twitter
    #Messenger().send_twitter_api_msg("Hello, this is a test Twitter message.")

    # Test Email
    #Messenger().send_email("Test message", "Hello this is a test email.")

    pass
