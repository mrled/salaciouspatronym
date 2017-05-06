# Salacious Patronym

turns out i have a very juvenile sense of humor

Salacious Patronym is a Twitter bot that turns names into jokes, such as

> Barrack's "Obama" 🍆

or

> Hillary's "Clinton" 😏

or

> George's "Bush" 💦

See it over at [@SalaciousPat](https://twitter.com/SalaciousPat)

## Installing

Requires Python 3.x and [tweepy](http://tweepy.readthedocs.io/en/v3.5.0/)

I tend to use `virtualenv` to manage third party Python libraries:

    python -m ensurepip
    python -m pip install virtualenv
    python -m virtualenv venv
    . venv/bin/activate
    pip install tweepy
    python ./salacious_patronym.py

I have some tests (ok fine, I have one test) that can be run with the built-in `unittest` module:

    python -m unittest discover

## Running

    (venv) bash> ./salacious_patronym.py --help
    usage: salacious_patronym.py [-h] [-d] [-i {no,init,reinit}]
                                 [--pantheondb PANTHEONDB]
                                 [--pantheontsv PANTHEONTSV] [--sext] [-t]
                                 [--get-twitter-access]
                                 [--consumertoken CONSUMERTOKEN]
                                 [--consumersecret CONSUMERSECRET]
                                 [--accesstoken ACCESSTOKEN]
                                 [--accesssecret ACCESSSECRET]
                                 [string]

    A template for writing a new Python3 command line tool

    positional arguments:
      string                If provided, instead of getting a random name from the
                            Pantheon, quotify the string

    optional arguments:
      -h, --help            show this help message and exit
      -d, --debug           Include debugging output
      -i {no,init,reinit}, --initialize {no,init,reinit}
                            Initialization mode: assume initialized, initialize if
                            not already, or drop-then-initialize
      --pantheondb PANTHEONDB
                            Path to sqlite database containing Pantheon data
                            (created if nonexistent)
      --pantheontsv PANTHEONTSV
                            Path to pantheon.tsv from
                            http://pantheon.media.mit.edu/about/datasets
      --sext                Include a sexting emoji ♋
      -t, --twitter         Post the output to Twitter. Must supply consumer token
                            and consumer secret, which are constants that come
                            from the Twitter application itself, as well as an
                            access token and access secret, which can be obtained
                            through OAuth with --get-twitter-access. See tweepy
                            documentation for more details.
      --get-twitter-access  Given the Twitter consumer token and secret, retrieve
                            an access token and secret, which can be used to post.
                            Return immediately without posting or printing a joke.
      --consumertoken CONSUMERTOKEN
                            Consumer token for posting to Twitter, also settable
                            via $TWITTER_CONSUMER_TOKEN
      --consumersecret CONSUMERSECRET
                            Consumer secret for posting to Twitter, also settable
                            via $TWITTER_CONSUMER_SECRET
      --accesstoken ACCESSTOKEN
                            Access token for posting to Twitter, also settable via
                            $TWITTER_ACCESS_TOKEN
      --accesssecret ACCESSSECRET
                            Access secret for posting to Twitter, also settable
                            via $TWITTER_ACCESS_SECRET
