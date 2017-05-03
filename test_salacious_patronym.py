#!/usr/bin/env python3

import logging
import sqlite3
import unittest

import salacious_patronym


class PantheonTestCase(unittest.TestCase):

    dburi = "file:TESTING_MEMORY_DB"
    testtable = 'testtable'
    create_table_statement = """CREATE TABLE testtable("en_curid", "name", "numlangs", "birthcity", "birthstate", "countryName", "countryCode", "countryCode3", "LAT", "LON", "continentName", "birthyear", "gender", "occupation", "industry", "domain", "TotalPageViews", "L_star", "StdDevPageViews", "PageViewsEnglish", "PageViewsNonEnglish", "AverageViews", "HPI")"""

    def setUp(self):
        self.dbconn = sqlite3.connect(self.dburi)
        self.curse = self.dbconn.cursor()
        salacious_patronym.log.setLevel(logging.NOTSET)

    def tearDown(self):
        self.dbconn.close()
        self.curse = None

    def test_pantheon_init_empty_db(self):
        pantheon = salacious_patronym.Pantheon(self.dbconn, tablename=self.testtable)
        pantheon.loaddb("./pantheon.tsv")

        self.curse.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='{}'".format(self.testtable))
        result = self.curse.fetchone()[0]
        self.assertEqual(result, self.create_table_statement)
