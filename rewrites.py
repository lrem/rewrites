#!/usr/bin/env python
"""
Rewrites
========

A tool for automatic, fuzzy-matched, rewriting of URLs.
"""
from flask import Flask
import flask
import argparse
import os.path
import re
from difflib import get_close_matches
try:
    from itertools import izip_longest as zip_longest
except:
    from itertools import zip_longest

APP = Flask(__name__)
CUTOFF = 0.8
AVAILABLE = []
BASENAMES = {}
NAMENOEXT = {}
MANUAL = []


def get_args(argv=None):
    """
    Process the command line, or supported, arguments.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    add = parser.add_argument
    add('available', help="path to a file with available urls")
    add('manual', help="path to a file with manual rewrite regexes")
    return parser.parse_args(argv)


def register_unique(dictionary, key, value):
    """
    If `key` is not in `dictionary`, set it to `value`, `None` otherwise.
    """
    if key in dictionary:
        dictionary[key] = None
    else:
        dictionary[key] = value


def noext(path):
    """
    Return base name of `path` without extension.
    """
    return os.path.splitext(os.path.basename(path))[0]


def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def setup(args):
    """
    Set all the globals according to provided configuration.
    """
    AVAILABLE.extend(map(str.strip, open(args.available).readlines()))
    for url in AVAILABLE:
        register_unique(BASENAMES, os.path.basename(url), url)
        register_unique(NAMENOEXT, noext(url), url)
    for old, new in grouper(map(str.strip, open(args.manual).readlines()), 2):
        MANUAL.append((re.compile(old), new))


def nearest_match(string, collection):
    """
    Try to find an unique match from `string` to `collection`.
    """
    if string in collection:
        return string
    close = get_close_matches(string, collection)
    if len(close) == 1:
        return close[0]
    return None


@APP.route('/<path:req_path>')
def rewrite(req_path):
    """
    301 redirect to the nearest good match for `req_path`.
    Return 404 if no good match available.
    """
    if len(AVAILABLE) == 0:
        setup(get_args())
    for rule in MANUAL:
        req_path = re.sub(rule[0], rule[1], req_path)
    match = nearest_match(req_path, AVAILABLE)
    if match is None:
        match = nearest_match(os.path.basename(req_path), BASENAMES.keys())
        if match:
            match = BASENAMES[match]
    if match is None:
        match = nearest_match(noext(req_path), NAMENOEXT.keys())
        if match:
            match = NAMENOEXT[match]
    if match is None:
        flask.abort(404)
    return flask.redirect(match)


if __name__ == '__main__':
    setup(get_args())
    APP.run(debug=True)
