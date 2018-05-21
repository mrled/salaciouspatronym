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

scriptdir = os.path.dirname(os.path.realpath(__file__))


# Helper functions


def resolvepath(path):
    return os.path.realpath(os.path.normpath(os.path.expanduser(path)))


def getoptenv(name):
    """Return the value of an environment variable if it exists, or an empty string otherwise
    """
    try:
        return os.environ[name]
    except KeyError:
        return ""


# Implementation functions


class Quotify:
    """A joke-making factory
    """

    sextemoji = ['🍆', '💦', '🍑', '😏', '🤤', '🙈', '👉👌', '🍌', '♋']

    def __init__(self, pantheon):
        """Initialize the joke-making factory

        pantheon        An instance of the Pantheon class
        """
        self.pantheon = pantheon

    @classmethod
    def quotify(cls, string, sext=False, after_newline=""):
        """Make a morally bankrupt joke from an input string

        u see, the joke is that if you put something in quotes, it makes it sound dirty

        string          The input string. Must have at least one space
        sext            If if True, add a sext emoji like the eggplant
        after_newline   If passed, append this argument as text to our morally bankrupt joke
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

        if after_newline:
            output = "{}\n{}".format(output, after_newline)

        return output

    @classmethod
    def randomsextemoji(cls):
        """Retrieve a random sext emoji
        """
        idx = random.randint(0, len(cls.sextemoji) -1)
        return cls.sextemoji[idx]

    def randomname(self, sext=False):
        """Retrieve a random, but suitable-for-joke-making, Pantheon name
        """
        suitable = False
        while not suitable:
            deity = self.pantheon.randomusa()
            splitname = deity['name'].split(' ')
            if len(splitname) == 2:
                suitable = True
        return self.quotify(
            deity['name'],
            sext=sext,
            after_newline=self.pantheon.geturl(deity['en_curid']))


class Pantheon:
    """A Pantheon database
    """

    tsvuri = "http://pantheon.media.mit.edu/pantheon.tsv"

    def __init__(self, connection, tablename="pantheon"):
        """Initialize the Pantheon database

        connection      A database connection to the Pantheon database
        tablename       The name of the table containing entries in the Pantheon
        """
        self.connection = connection
        self.connection.row_factory = sqlite3.Row
        self.tablename = tablename

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
        logging.debug("Wikipedia API response:\n{}".format(
            json.dumps(wikimd, indent=2, sort_keys=True)))
        return wikimd['query']['pages'][str(curid)]['fullurl']

    @property
    def initialized(self):
        """Determine whether the database has been initialized
        """
        curse = self.connection.cursor()
        curse.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='{}'".format(
                self.tablename))
        return bool(curse.fetchone())

    def loaddb(self, tsvpath):
        """Load the database from the tsv

        tsvpath     The location of the Pantheon TSV file
        """
        curse = self.connection.cursor()
        with open(resolvepath(tsvpath), encoding='utf-8') as tsvfile:
            tsvreader = csv.reader(tsvfile, delimiter='\t')
            columns = None
            ctr=0
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
                ctr += 1
        logging.debug("Added {} deities to the pantheon database".format(ctr))
        self.connection.commit()

    def randomusa(self):
        """Retrieve a random entry that was born in the US
        """
        curse = self.connection.cursor()
        curse.execute(
            "SELECT * FROM ? WHERE countryCode='US' ORDER BY RANDOM() LIMIT 1",
            (self.tablename, ))
        result = curse.fetchone()
        curse.close()
        return result


def log_auth_tokens(consumertoken, consumersecret):
    """Retrieve and log Twitter authentication tokens

    consumertoken       A Twitter consumer token
    consumersecret      A Twitter consumer secret
    """
    auth = tweepy.OAuthHandler(consumertoken, consumersecret)
    redirect_url = auth.get_authorization_url()
    verifier = input(' '.join([
        "Go to <{}> in your browser,".format(redirect_url),
        "log in as the account you want to use for the bot,",
        "and paste the PIN here: "]))
    auth.get_access_token(verifier)
    logging.info("\n".join([
        "Authentication successful",
        "    access token:  {}".format(auth.access_token),
        "    access secret: {}".format(auth.access_token_secret)]))


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


def parseargs(*args, **kwargs):
    """Parse command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="A childish joke that I've automated so now it can live on forever")
    parser.add_argument(
        "-d", "--debug", action='store_true',
        help="Include debugging output")
    parser.add_argument(
        "-i", "--initialize",
        choices=['no', 'init', 'reinit'], default='no',
        help=(
            "Initialization mode: assume initialized, "
            "initialize if not already, or drop-then-initialize"))
    parser.add_argument(
        "--pantheondb", default=os.path.join(scriptdir, "pantheon.sqlite"),
        help="Path to sqlite database containing Pantheon data (created if nonexistent)")
    parser.add_argument(
        "--pantheontsv", default=os.path.join(scriptdir, 'pantheon.tsv'),
        help="Path to pantheon.tsv from http://pantheon.media.mit.edu/about/datasets")
    parser.add_argument(
        "--sext", action='store_true',
        help="Append a sexting emoji (one of {})".format(', '.join(Quotify.sextemoji)))

    parser.add_argument(
        "-t", "--tweet", action='store_true',
        help=(
            "Post the output to Twitter. Must supply consumer token and consumer secret, "
            "which are constants that come from the Twitter application itself, "
            "as well as an access token and access secret, "
            "which can be obtained through OAuth with --get-twitter-access. "
            "See tweepy documentation for more details."))
    parser.add_argument(
        "--get-twitter-access", action='store_true', dest="gettwaccess",
        help=(
            "Given the Twitter consumer token and secret, retrieve an access token and secret, "
            "which can be used to post. Return immediately without posting or printing a joke."))
    parser.add_argument(
        "--test-twitter-access", action='store_true', dest="testtwaccess",
        help=(
            "Test whether the Twitter credentials work - "
            "exit zero if they work properly or nonzero if authentication fails"))
    parser.add_argument(
        "--consumertoken", default=getoptenv("SALLYPAT_CONSUMERTOKEN"),
        help="Consumer token for posting to Twitter, also settable via $SALLYPAT_CONSUMERTOKEN")
    parser.add_argument(
        "--consumersecret", default=getoptenv("SALLYPAT_CONSUMERSECRET"),
        help="Consumer secret for posting to Twitter, also settable via $SALLYPAT_CONSUMERSECRET")
    parser.add_argument(
        "--accesstoken", default=getoptenv("SALLYPAT_ACCESSTOKEN"),
        help="Access token for posting to Twitter, also settable via $SALLYPAT_ACCESSTOKEN")
    parser.add_argument(
        "--accesssecret", default=getoptenv("SALLYPAT_ACCESSSECRET"),
        help="Access secret for posting to Twitter, also settable via $SALLYPAT_ACCESSSECRET")

    parser.add_argument(
        "string", nargs='?',
        help=(
            "If present, make the joke with the string; "
            "otherwise, get the name of a random famous person from the Pantheon "
            "and quotify that instead"))

    parsed = parser.parse_args(*args, **kwargs)

    return parsed


def aws_lambda_handler(event, context):
    """Entrypoint for AWS Lambda use

    Assumptions
    - The Pantheon sqlite database has already been initialized
    - A sexting emoji is always appended
    """
    logging.basicConfig()
    logging.debug("AWS Lambda event handler fired; event is '{}'; context is '{}'".format(
        event, context))

    parsed = parseargs()
    connection = sqlite3.connect(parsed.pantheondb)
    pantheon = Pantheon(connection)
    qq = Quotify(pantheon)

    if event:
        if 'source' in event and event['source'] == 'aws.events':
            joek = qq.randomname(sext=True)
            logging.info("Wrote a very original joek: {}".format(joek))
            api = authenticate(parsed.consumertoken, parsed.consumersecret, parsed.accesstoken, parsed.accesssecret)
            api.update_status(joek)
        else:
            raise Exception("Passed an event but it was not from a source we understand")
    else:
        raise Exception("No event passed")


def main(*args, **kwargs):
    """Entrypoint for command-line use
    """
    logging.basicConfig()
    parsed = parseargs(*args, **kwargs)

    if parsed.debug:
        logging.root.setLevel(logging.DEBUG)

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

    if parsed.testtwaccess:
        try:
            api = authenticate(
                parsed.consumertoken, parsed.consumersecret, parsed.accesstoken,
                parsed.accesssecret)
            api.home_timeline()
            logging.info("Twitter authentication successful")
            return 0
        except tweepy.error.TweepError as exc:
            logging.error("Twitter authentication failed: {}".format(exc))
            return -1

    if parsed.tweet or parsed.gettwaccess:
        if not parsed.consumertoken or not parsed.consumersecret:
            logging.error(
                "Could not get twitter access: missing consumer token and/or consumer secret")
            return -1

    if parsed.gettwaccess:
        log_auth_tokens(parsed.consumertoken, parsed.consumersecret)
        return 0

    print(joek)

    if parsed.tweet:
        api = authenticate(
            parsed.consumertoken, parsed.consumersecret, parsed.accesstoken, parsed.accesssecret)
        api.update_status(joek)


if __name__ == '__main__':
    sys.exit(main(*sys.argv))
