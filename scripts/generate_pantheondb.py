#!/usr/bin/env python3

import csv
import os
import sqlite3

scriptsdir = os.path.dirname(__file__)
repodir = os.path.dirname(scriptsdir)
packagedir = os.path.join(repodir, "salaciouspatronym")
pantheontsv = os.path.join(repodir, "vendor", "pantheon", "pantheon.tsv")

# Must be in the package directory for importlib to find it
pantheondb = os.path.join(packagedir, "pantheon.sqlite")

# Must match what's in the Pantheon class in the application
tablename = "pantheon"

if os.path.exists(pantheondb):
    os.unlink(pantheondb)

connection = sqlite3.connect(pantheondb)
curse = connection.cursor()

with open(pantheontsv, encoding="utf-8") as tsvfile:
    tsvreader = csv.reader(tsvfile, delimiter="\t")
    columns = None
    ctr = 0
    initialized = False
    for row in tsvreader:
        # SQL-escape quotes which might occur in nicknames
        escapedrow = [x.replace('"', '""') for x in row]
        # wrap each field in double quotes to handle spaces
        quotedrow = ['"{}"'.format(x) for x in escapedrow]

        # First row in the file is the column names; subsequent rows are data
        if not columns:
            columns = quotedrow
            curse.execute("CREATE TABLE {} ({})".format(tablename, ", ".join(columns)))
        else:
            curse.execute(
                "INSERT INTO {} VALUES ({})".format(tablename, ", ".join(quotedrow))
            )
        ctr += 1

connection.commit()
