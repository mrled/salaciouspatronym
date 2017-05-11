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

    A childish joke that I've automated so now it can live on forever

    positional arguments:
      string                If present, make the joke with the string; otherwise,
                            get the name of a random famous person from the
                            Pantheon and quotify that instead

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
      -t, --tweet           Post the output to Twitter. Must supply consumer token
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

## Docker concerns

I run this in Docker

When building the image on Windows, special care must be taken to avoid Windows line endings, which BusyBox's /bin/sh cannot handle. This is a problem because the default Git configuration on Windows is to convert any Unix line endings in the repo to Windows line endings on checkout, and then convert them back to Unix line endings on commit. To deal with this make sure that `core.autocrlf` is set to `false` for this repository.

### Building for production

Docker supports [pulling a Git repo and building its contents](https://docs.docker.com/engine/reference/commandline/build/#git-repositories):

    docker build https://github.com/mrled/salaciouspatronym

This builds the latest commit on the master branch, which (ideally) contains the latest working copy of the code, based on the Dockerfile in the root of the repo

### Building during development

To build during development, check out the code locally, change directory to the checkout location, and then tell Docker to build the current directory

    docker build .

This lets you make local changes and build a Docker image incorporating them for testing, before pushing to the master branch.
