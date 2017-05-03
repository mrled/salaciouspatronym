#!/usr/bin/env python3

import argparse
import csv
import logging
import os
import sys
import sqlite3


log = logging.getLogger(__name__)
scriptdir = os.path.dirname(os.path.realpath(__file__))


# Helper functions


def resolvepath(path):
    return os.path.realpath(os.path.normpath(os.path.expanduser(path)))


# Implementation functions


def quote_unquote(string):
    split = string.split(' ')
    if len(string) < 1 or len(split):
        raise Exception("u can't make joek without sum nput dude")
    elif len(split) == 1:
        return '"{}", lol'.format(string)
    else:
        return '{}\'s "{}"'.format(split[0], split[1:])


class Pantheon:

    def __init__(self, connection, tablename="pantheon"):
        self.connection = connection
        self.tablename = tablename

    @property
    def initialized(self):
        curse = self.connection.cursor()
        curse.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='{}'".format(
                self.tablename))
        return bool(curse.fetchone())

    def loaddb(self, tsvpath):
        """
        Pantheon is loaded from the 'pantheon.tsv' file found here:
        http://pantheon.media.mit.edu/about/datasets
        """
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
    parsed = parser.parse_args()

    if parsed.debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
    parsed.pantheondb = resolvepath(parsed.pantheondb)
    parsed.pantheontsv = resolvepath(parsed.pantheontsv)

    if parsed.initialize == 'reinit' and os.path.exists(parsed.pantheondb):
        os.unlink(parsed.pantheondb)

    connection = sqlite3.connect(parsed.pantheondb)
    pantheon = Pantheon(connection)

    if parsed.initialize == 'reinit' or parsed.initialize == 'init':
        pantheon.loaddb(parsed.pantheontsv)


if __name__ == '__main__':
    sys.exit(main(*sys.argv))
