#!/usr/bin/env python3

import argparse
import csv
import json
import logging
import os
import random
import sys
import sqlite3
import urllib.request

import tweepy

log = logging.getLogger(__name__)
scriptdir = os.path.dirname(os.path.realpath(__file__))


# Helper functions


def resolvepath(path):
    return os.path.realpath(os.path.normpath(os.path.expanduser(path)))


def getoptenv(name):
    """Return the value of an environment variable if it exists, or an empty string otherwise"""
    try:
        return os.environ[name]
    except KeyError:
        return ""


# Implementation functions


class Quotify:

    sextemoji = ['🍆', '💦', '🍑', '😏', '🤤', '🙈', '👉👌', '🍌', '♋']

    def __init__(self, pantheon):
        self.pantheon = pantheon

    @classmethod
    def quotify(cls, string, sext=False, afterNewline=""):
        """Make a morally bankrupt joke from an input string
        u see, the joke is that if you put something in quotes, it makes it sound dirty
        string: The input string. Must have at least one space
        sext: If if True, add a sext emoji like the eggplant
        afterNewline: If passed, after making our morally bankrupt joke, append this argument as text
        """
        split = string.split(' ')
        output = ""
        if len(string) < 1 or len(split) < 1:
            raise Exception("u can't make joek without sum nput dude")
        elif len(split) == 1:
            output = '"{}", lol'.format(string)
        else:
            fname = split[0]
            possessive = "'s" if fname[-1] != 's' else "'"
            lname = " ".join(split[1:])
            output = '{}{} "{}"'.format(fname, possessive, lname)

        if sext:
            output += " {}".format(cls.randomsextemoji())

        if afterNewline:
            output = "{}\n{}".format(output, afterNewline)

        return output

    @classmethod
    def randomsextemoji(cls):
        idx = random.randint(0, len(cls.sextemoji) -1)
        return cls.sextemoji[idx]

    def randomname(self, sext=False):
        suitable = False
        while not suitable:
            deity = self.pantheon.randomusa()
            splitname = deity['name'].split(' ')
            if len(splitname) == 2:
                suitable = True
        return self.quotify(
            deity['name'],
            sext=sext,
            afterNewline=self.pantheon.geturl(deity['en_curid']))


class Pantheon:

    tsvuri = "http://pantheon.media.mit.edu/pantheon.tsv"

    def __init__(self, connection, tablename="pantheon"):
        self.connection = connection
        self.connection.row_factory = sqlite3.Row
        self.tablename = tablename

    @classmethod
    def geturl(cls, curid):
        """Get the Wikipedia URL from the curid
        - https://en.wikipedia.org/w/api.php?action=query&prop=info&pageids=[CURID]&inprop=url&format=json
        - Could just do http://en.wikipedia.org/?curid=[CURID] however this won't redirect to a nice URL with the name
        """
        url = "https://en.wikipedia.org/w/api.php?action=query&prop=info&pageids={}&inprop=url&format=json".format(curid)
        apiresponse = urllib.request.urlopen(url).read()
        wikimd = json.loads(apiresponse.decode())
        return wikimd['query']['pages'][str(curid)]['fullurl']

    @property
    def initialized(self):
        curse = self.connection.cursor()
        curse.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='{}'".format(
                self.tablename))
        return bool(curse.fetchone())

    def loaddb(self, tsvpath):
        """Load the database from the tsv"""
        curse = self.connection.cursor()
        with open(resolvepath(tsvpath), encoding='utf-8') as tsvfile:
            tsvreader = csv.reader(tsvfile, delimiter='\t')
            columns = None
            for row in tsvreader:
                # SQL-escape quotes which might occur in nicknames
                escapedrow = [x.replace('"', '""') for x in row]
                # wrap each field in double quotes to handle spaces
                quotedrow = ['"{}"'.format(x) for x in escapedrow]

                # First row in the file is the column names; subsequent rows are data
                if not columns:
                    columns = quotedrow
                    if not self.initialized:
                        curse.execute("CREATE TABLE {}({})".format(
                            self.tablename, ", ".join(columns)))
                else:
                    curse.execute("INSERT INTO {} VALUES ({})".format(
                        self.tablename, ", ".join(quotedrow)))
        self.connection.commit()

    def randomusa(self):
        curse = self.connection.cursor()
        curse.execute(
            "SELECT * FROM {} WHERE countryCode='US' ORDER BY RANDOM() LIMIT 1".format(self.tablename))
        result = curse.fetchone()
        curse.close()
        return result


def retrieve_auth_tokens(consumertoken, consumersecret):
    auth = tweepy.OAuthHandler(consumertoken, consumersecret)
    redirect_url = auth.get_authorization_url()
    verifier = input(
        "Go to <{}> in your browser, log in as the account you want to use for the bot, and paste the PIN here: ".format(
            redirect_url))
    auth.get_access_token(verifier)
    print("\n".join([
        "Authentication successful",
        "    access token:  {}".format(auth.access_token),
        "    access secret: {}".format(auth.access_token_secret)]))


def authenticate(consumertoken, consumersecret, accesstoken, accesssecret):
    auth = tweepy.OAuthHandler(consumertoken, consumersecret)
    auth.set_access_token(accesstoken, accesssecret)
    api = tweepy.API(auth)
    return api


def main(*args, **kwargs):
    parser = argparse.ArgumentParser(
        description="A childish joke that I've automated so now it can live on forever")
    parser.add_argument(
        "-d", "--debug", action='store_true',
        help="Include debugging output")
    parser.add_argument(
        "-i", "--initialize",
        choices=['no', 'init', 'reinit'], default='no',
        help="Initialization mode: assume initialized, initialize if not already, or drop-then-initialize")
    parser.add_argument(
        "--pantheondb", default=os.path.join(scriptdir, "pantheon.sqlite"),
        help="Path to sqlite database containing Pantheon data (created if nonexistent)")
    parser.add_argument(
        "--pantheontsv", default=os.path.join(scriptdir, 'pantheon.tsv'),
        help="Path to pantheon.tsv from http://pantheon.media.mit.edu/about/datasets")
    parser.add_argument(
        "--sext", action='store_true',
        help="Include a sexting emoji {}".format(Quotify.randomsextemoji()))

    parser.add_argument(
        "-t", "--tweet", action='store_true',
        help="Post the output to Twitter. Must supply consumer token and consumer secret, which are constants that come from the Twitter application itself, as well as an access token and access secret, which can be obtained through OAuth with --get-twitter-access. See tweepy documentation for more details.")
    parser.add_argument(
        "--get-twitter-access", action='store_true', dest="gettwaccess",
        help="Given the Twitter consumer token and secret, retrieve an access token and secret, which can be used to post. Return immediately without posting or printing a joke.")
    parser.add_argument(
        "--consumertoken", default=getoptenv("SALACIOUSPATRONYM_CONSUMERTOKEN"),
        help="Consumer token for posting to Twitter, also settable via $SALACIOUSPATRONYM_CONSUMERTOKEN")
    parser.add_argument(
        "--consumersecret", default=getoptenv("SALACIOUSPATRONYM_CONSUMERSECRET"),
        help="Consumer secret for posting to Twitter, also settable via $SALACIOUSPATRONYM_CONSUMERSECRET")
    parser.add_argument(
        "--accesstoken", default=getoptenv("SALACIOUSPATRONYM_ACCESSTOKEN"),
        help="Access token for posting to Twitter, also settable via $SALACIOUSPATRONYM_ACCESSTOKEN")
    parser.add_argument(
        "--accesssecret", default=getoptenv("SALACIOUSPATRONYM_ACCESSSECRET"),
        help="Access secret for posting to Twitter, also settable via $SALACIOUSPATRONYM_ACCESSSECRET")

    parser.add_argument(
        "string", nargs='?',
        help="If present, make the joke with the string; otherwise, get the name of a random famous person from the Pantheon and quotify that instead")
    parsed = parser.parse_args()

    if parsed.debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    if parsed.string:
        joek = Quotify.quotify(parsed.string, sext=parsed.sext)
    else:
        parsed.pantheondb = resolvepath(parsed.pantheondb)
        parsed.pantheontsv = resolvepath(parsed.pantheontsv)

        if parsed.initialize == 'reinit' and os.path.exists(parsed.pantheondb):
            os.unlink(parsed.pantheondb)

        connection = sqlite3.connect(parsed.pantheondb)
        pantheon = Pantheon(connection)

        if parsed.initialize == 'reinit' or parsed.initialize == 'init':
            if not os.path.exists(parsed.pantheontsv):
                urllib.request.urlretrieve(pantheon.tsvuri, parsed.pantheontsv)
            pantheon.loaddb(parsed.pantheontsv)

        qq = Quotify(pantheon)
        joek = qq.randomname(sext=parsed.sext)

    if not parsed.gettwaccess:
        print(joek)

    if parsed.tweet or parsed.gettwaccess:
        if not parsed.consumertoken or not parsed.consumersecret:
            raise Exception("Could not get twitter access: missing consumer token and/or consumer secret")

    if parsed.gettwaccess:
        retrieve_auth_tokens(parsed.consumertoken, parsed.consumersecret)
        return

    if parsed.tweet:
        if not parsed.accesstoken or not parsed.accesssecret:
            raise Exception("Could not get twitter access: missing access token and/or access secret")
        api = authenticate(parsed.consumertoken, parsed.consumersecret, parsed.accesstoken, parsed.accesssecret)
        api.update_status(joek)


if __name__ == '__main__':
    sys.exit(main(*sys.argv))
