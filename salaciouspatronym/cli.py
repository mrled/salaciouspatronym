import argparse
import logging
import os
import pdb
import sys
import traceback
import typing

from tweepy import TweepyException

from salaciouspatronym import (
    Pantheon,
    Quotify,
    authenticate,
    log_auth_tokens,
)
from salaciouspatronym.applogger import AppLogger


def idb_excepthook(type, value, tb):
    """Call an interactive debugger in post-mortem mode

    If you do "sys.excepthook = idb_excepthook", then an interactive debugger
    will be spawned at an unhandled exception
    """
    if hasattr(sys, "ps1") or not sys.stderr.isatty():
        sys.__excepthook__(type, value, tb)
    else:
        traceback.print_exception(type, value, tb)
        print
        pdb.pm()


sys.excepthook = idb_excepthook


def parseargs(args: typing.List):
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="A childish joke that I've automated so now it can live on forever"
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Include verbose output, start debugger on unhandled exception",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Include verbose output"
    )
    parser.add_argument(
        "--emoji",
        action="store_true",
        help="Append a sexting emoji (one of {})".format(", ".join(Quotify.sextemoji)),
    )

    parser.add_argument(
        "-t",
        "--tweet",
        action="store_true",
        help=(
            "Post the output to Twitter. Must supply consumer token and consumer secret, "
            "which are constants that come from the Twitter application itself, "
            "as well as an access token and access secret, "
            "which can be obtained through OAuth with --get-twitter-access. "
            "See tweepy documentation for more details."
        ),
    )
    parser.add_argument(
        "--get-twitter-access",
        action="store_true",
        dest="gettwaccess",
        help=(
            "Given the Twitter consumer token and secret, retrieve an access token and secret, "
            "which can be used to post. Return immediately without posting or printing a joke."
        ),
    )
    parser.add_argument(
        "--test-twitter-access",
        action="store_true",
        dest="testtwaccess",
        help=(
            "Test whether the Twitter credentials work - "
            "exit zero if they work properly or nonzero if authentication fails"
        ),
    )
    parser.add_argument(
        "--consumertoken",
        default=os.environ.get("SALLYPAT_CONSUMERTOKEN"),
        help="Consumer token for posting to Twitter, also settable via $SALLYPAT_CONSUMERTOKEN",
    )
    parser.add_argument(
        "--consumersecret",
        default=os.environ.get("SALLYPAT_CONSUMERSECRET"),
        help="Consumer secret for posting to Twitter, also settable via $SALLYPAT_CONSUMERSECRET",
    )
    parser.add_argument(
        "--accesstoken",
        default=os.environ.get("SALLYPAT_ACCESSTOKEN"),
        help="Access token for posting to Twitter, also settable via $SALLYPAT_ACCESSTOKEN",
    )
    parser.add_argument(
        "--accesssecret",
        default=os.environ.get("SALLYPAT_ACCESSSECRET"),
        help="Access secret for posting to Twitter, also settable via $SALLYPAT_ACCESSSECRET",
    )

    parser.add_argument(
        "string",
        nargs="?",
        help=(
            "If present, make the joke with the string; "
            "otherwise, get the name of a random famous person from the Pantheon "
            "and quotify that instead"
        ),
    )

    parsed = parser.parse_args(args)

    return parsed


def main():
    """Entrypoint for command-line use"""
    parsed = parseargs(sys.argv[1:])

    if parsed.debug:
        sys.excepthook = idb_excepthook
    if parsed.debug or parsed.verbose:
        AppLogger.root.setLevel(logging.DEBUG)

    if parsed.string:
        joek = Quotify.quotify(parsed.string, emoji=parsed.emoji)
    else:
        pantheon = Pantheon()
        qq = Quotify(pantheon)
        joek = qq.randomname(emoji=parsed.emoji)

    if parsed.testtwaccess:
        try:
            api = authenticate(
                parsed.consumertoken,
                parsed.consumersecret,
                parsed.accesstoken,
                parsed.accesssecret,
            )
            api.home_timeline()
            AppLogger.info("Twitter authentication successful")
            return 0
        except TweepyException as exc:
            AppLogger.error("Twitter authentication failed: {}".format(exc))
            return -1

    if parsed.tweet or parsed.gettwaccess:
        if not parsed.consumertoken or not parsed.consumersecret:
            AppLogger.error(
                "Could not get twitter access: missing consumer token and/or consumer secret"
            )
            return -1

    if parsed.gettwaccess:
        log_auth_tokens(parsed.consumertoken, parsed.consumersecret)
        return 0

    print(joek)

    if parsed.tweet:
        api = authenticate(
            parsed.consumertoken,
            parsed.consumersecret,
            parsed.accesstoken,
            parsed.accesssecret,
        )
        api.update_status(joek)
