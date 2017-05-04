#!/usr/bin/env python3

import argparse
import csv
import logging
import os
import random
import sys
import sqlite3
import urllib.request


log = logging.getLogger(__name__)
scriptdir = os.path.dirname(os.path.realpath(__file__))


# Helper functions


def resolvepath(path):
    return os.path.realpath(os.path.normpath(os.path.expanduser(path)))


# Implementation functions


class Quotify:

    sextemoji = ['🍆', '💦', '🍑', '😏', '🤤', '🙈', '👉👌', '🍌', '♋']

    def __init__(self, pantheon):
        self.pantheon = pantheon

    @classmethod
    def quotify(cls, string, sext=False):
        split = string.split(' ')
        output = ""
        if len(string) < 1 or len(split) < 1:
            raise Exception("u can't make joek without sum nput dude")
        elif len(split) == 1:
            output = '"{}", lol'.format(string)
        else:
            output = '{}\'s "{}"'.format(split[0], " ".join(split[1:]))
        if sext:
            output += " {}".format(cls.randomsextemoji())
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
        return self.quotify(deity['name'], sext=sext)


class Pantheon:

    tsvuri = "http://pantheon.media.mit.edu/about/datasets"

    def __init__(self, connection, tablename="pantheon"):
        self.connection = connection
        self.connection.row_factory = sqlite3.Row
        self.tablename = tablename

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


# Main handler


def main(*args, **kwargs):
    parser = argparse.ArgumentParser(
        description="A template for writing a new Python3 command line tool")
    parser.add_argument(
        "-d", action='store_true', dest='debug',
        help="Include debugging output")
    parser.add_argument(
        "-i", "--initialize",
        choices=['no', 'init', 'reinit'], default='no',
        help="Initialization mode: assume initialized, initialized if not already, or drop-then-initialize")
    parser.add_argument(
        "-p", "--pantheondb",
        default=os.path.join(scriptdir, "pantheon.sqlite"),
        help="Path to sqlite database containing Pantheon data (created if nonexistent)")
    parser.add_argument(
        "-t", "--pantheontsv", default=os.path.join(scriptdir, 'pantheon.tsv'),
        help="Path to pantheon.tsv from http://pantheon.media.mit.edu/about/datasets")
    parser.add_argument(
        "-s", "--sext", action='store_true',
        help="Include a sexting emoji {}".format(Quotify.randomsextemoji()))
    parser.add_argument(
        "string", nargs='?',
        help="If provided, instead of getting a random name from the Pantheon, quotify the string")
    parsed = parser.parse_args()

    if parsed.debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    if parsed.string:
        print(Quotify.quotify(parsed.string, sext=parsed.sext))
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
        print(qq.randomname(sext=parsed.sext))


if __name__ == '__main__':
    sys.exit(main(*sys.argv))
