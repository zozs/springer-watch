#!/usr/bin/env python3

import feedparser
import json
import smtplib

from email.mime.text import MIMEText


CONFIG_FILE = 'config.json'
EMAIL_MESSAGE = """\
Hi,

The following new proceedings are now available on SpringerLink:

{}

Regards,
springer-watch
"""

# We store all seen GUIDs for everything, and then react if we see something
# new. In this way we can have a global GUID list without caring about which
# proceedings old ones belong to.

def load_settings(filename):
    """Load settings from JSON and returns config object."""
    with open(filename) as f:
        config = json.load(f)
        return config


def save_settings(config, filename):
    """Save settings to JSON."""
    with open(filename, 'w') as f:
        json.dump(config, f, indent=2)


def get_feed(conference):
    """Creates and parses an RSS feed given a conference name."""
    url = 'http://link.springer.com/search.rss?query={}&facet-content-type=%22Book%22'.format(conference)
    return feedparser.parse(url)


def check_new_guids(conference, guids):
    """Returns a list of feeditem for new guids."""
    feed = get_feed(conference)
    new = [item for item in feed['items'] if item.id not in guids]
    return new


def updates_email(new, config):
    """Construct e-mail with new items and send to email address."""
    item_fmt = '{}\n{}\n'
    subject = '[springer-watch] {:d} new proceedings'.format(len(new))
    new_msgs = '\n'.join(item_fmt.format(item.title, item.link) for item in new)
    message_text = EMAIL_MESSAGE.format(new_msgs)

    # Construct actual e-mail and send it.
    message = MIMEText(message_text)
    message['Subject'] = subject
    message['From'] = config['sender']
    message['To'] = config['email']

    # Now send it.
    smtp = smtplib.SMTP(config['smtp']['host'], port=config['smtp']['port'])
    smtp.send_message(message)
    smtp.quit()


def check_conferences(config):
    """Checks all conferences for new GUIDs."""
    new = []
    for c in config['proceedings']:
        new.extend(check_new_guids(c, config['guid']))
    
    if len(new) > 0:
        # Handle all new by creating an e-mail.
        updates_email(new, config)

        # Store new GUIDs.
        for item in new:
            config['guid'].append(item.id)


if __name__ == '__main__': 
    config = load_settings(CONFIG_FILE)
    check_conferences(config)
    save_settings(config, CONFIG_FILE)
