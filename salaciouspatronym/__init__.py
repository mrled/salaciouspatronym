#!/usr/bin/env python3

import json
import logging
import os
import random
import sqlite3
import typing
import urllib.request
from importlib.resources import path as resource_path

import tweepy

from salaciouspatronym.applogger import AppLogger


class Quotify:
    """A joke-making factory"""

    # sextemoji = ["🍆", "💦", "🍑", "😏", "🤤", "🙈", "👉👌", "🍌", "♋"]
    sextemoji = ["🍆", "💦", "🍑", "😏", "🤤", "👉👌", "♋", "😳"]

    def __init__(self, pantheon):
        """Initialize the joke-making factory

        pantheon        An instance of the Pantheon class
        """
        self.pantheon = pantheon

    @classmethod
    def quotify(cls, string, emoji=False, after_newline=""):
        """Make a morally bankrupt joke from an input string

        u see, the joke is that if you put something in quotes, it makes it sound dirty

        string          The input string. Must have at least one space
        emoji           If if True, add a sext emoji like the eggplant
        after_newline   If passed, append this argument as text to our morally bankrupt joke
        """
        split = string.split(" ")
        output = ""
        if len(string) < 1 or len(split) < 1:
            raise Exception("u can't make joek without sum nput dude")
        elif len(split) == 1:
            output = '"{}", lol'.format(string)
        else:
            fname = split[0]
            possessive = "'s" if fname[-1] != "s" else "'"
            lname = " ".join(split[1:])
            output = '{}{} "{}"'.format(fname, possessive, lname)

        if emoji:
            output += " {}".format(cls.randomsextemoji())

        if after_newline:
            output = "{}\n{}".format(output, after_newline)

        return output

    @classmethod
    def randomsextemoji(cls):
        """Retrieve a random sext emoji"""
        idx = random.randint(0, len(cls.sextemoji) - 1)
        return cls.sextemoji[idx]

    def randomname(self, emoji=False):
        """Retrieve a random, but suitable-for-joke-making, Pantheon name"""
        suitable = False
        while not suitable:
            deity = self.pantheon.randomusa()
            splitname = deity["name"].split(" ")
            if len(splitname) == 2:
                suitable = True
        return self.quotify(
            deity["name"],
            emoji=emoji,
            after_newline=self.pantheon.geturl(deity["en_curid"]),
        )


class Pantheon:
    """A Pantheon database"""

    # Must match what's in scripts/generate_pantheondb.py
    tablename = "pantheon"

    # This is the package resource path...
    # should match the package_data item in setup.py
    # and the path that scripts/generate_pantheondb.py saves to
    db_resource_path = "pantheon.sqlite"

    @classmethod
    def geturl(cls, curid):
        """Get the Wikipedia URL from the curid

        - https://en.wikipedia.org/w/api.php?action=query&prop=info&pageids=[CURID]&inprop=url&format=json
        - Could just do http://en.wikipedia.org/?curid=[CURID], however,
          this won't redirect to a nice URL with the name

        curid       An identifier corresponding to the Wikipedia page for a Pantheon entry
        """
        urltemplate = "https://en.wikipedia.org/w/api.php?action=query&prop=info&pageids={}&inprop=url&format=json"
        url = urltemplate.format(curid)
        apiresponse = urllib.request.urlopen(url).read()
        wikimd = json.loads(apiresponse.decode())
        AppLogger.debug(
            "Wikipedia API response:\n{}".format(
                json.dumps(wikimd, indent=2, sort_keys=True)
            )
        )
        return wikimd["query"]["pages"][str(curid)]["fullurl"]

    def query(self, sql: str, params: typing.Optional[typing.Iterable] = None):
        """Query the Pantheon database"""
        if not params:
            params = []
        with resource_path(__name__, self.db_resource_path) as dbpath:
            AppLogger.debug(f"Using database found at {dbpath}...")
            stat_sp = os.stat("/var/lang/lib/python3.9/site-packages/salaciouspatronym")
            AppLogger.debug(f"Package dir stat: {stat_sp}")
            stat_db = os.stat(
                "/var/lang/lib/python3.9/site-packages/salaciouspatronym/pantheon.sqlite"
            )
            AppLogger.debug(f"Database stat: {stat_db}")
            connection = sqlite3.connect(dbpath)
            connection.row_factory = sqlite3.Row
            curse = connection.cursor()
            curse.execute(sql, params)
            result = curse.fetchall()
            return result

    def randomusa(self):
        """Retrieve a random entry that was born in the US"""
        result = self.query(
            f"SELECT * FROM {self.tablename} WHERE countryCode='US' ORDER BY RANDOM() LIMIT 1",
        )
        return result[0]


def log_auth_tokens(consumertoken, consumersecret):
    """Retrieve and log Twitter authentication tokens

    consumertoken       A Twitter consumer token
    consumersecret      A Twitter consumer secret
    """
    auth = tweepy.OAuthHandler(consumertoken, consumersecret)
    redirect_url = auth.get_authorization_url()
    verifier = input(
        " ".join(
            [
                "Go to <{}> in your browser,".format(redirect_url),
                "log in as the account you want to use for the bot,",
                "and paste the PIN here: ",
            ]
        )
    )
    auth.get_access_token(verifier)
    AppLogger.info(
        "\n".join(
            [
                "Authentication successful",
                "    access token:  {}".format(auth.access_token),
                "    access secret: {}".format(auth.access_token_secret),
            ]
        )
    )


def authenticate(consumertoken, consumersecret, accesstoken, accesssecret):
    """Retrieve an authenticated tweepy.API instance

    consumertoken       A Twitter consumer token
    consumersecret      A Twitter consumer secret
    accesstoken         A Twitter access token
    accesssecret        A Twitter access secret
    """
    auth = tweepy.OAuthHandler(consumertoken, consumersecret)
    auth.set_access_token(accesstoken, accesssecret)
    api = tweepy.API(auth)
    return api


def aws_lambda_handler(event, context):
    """Entrypoint for AWS Lambda use

    Assumptions
    - The Pantheon sqlite database has already been initialized
    - A sexting emoji is always appended
    """
    AppLogger.setLevel(logging.DEBUG)
    AppLogger.info(
        "AWS Lambda event handler fired; event is '{}'; context is '{}'".format(
            event, context
        )
    )

    pantheon = Pantheon()
    qq = Quotify(pantheon)

    joek = qq.randomname(emoji=True)
    AppLogger.info("Wrote a very original joek: {}".format(joek))
    api = authenticate(
        os.environ.get("SALLYPAT_CONSUMERTOKEN"),
        os.environ.get("SALLYPAT_CONSUMERSECRET"),
        os.environ.get("SALLYPAT_ACCESSTOKEN"),
        os.environ.get("SALLYPAT_ACCESSSECRET"),
    )
    api.update_status(joek)
