#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SOBS - Simple OBject Storage

from flask import (Flask, render_template, request, make_response, Response, abort, send_file, redirect, url_for, safe_join)
from argparse import ArgumentParser
from uuid import uuid4
from os.path import abspath,dirname,basename,join,isfile,isdir
from os import makedirs
from hashlib import md5
from datetime import datetime

app = Flask(__name__)
#app.debug = True
ROOT=None
TMP=None

@app.route('/store', methods=[ 'PUT' ])
def store():
    uri = request.args.get('uri', None)
    path = request.args.get('path', None)
    hash = request.args.get('hash', None)

    if uri and path:
        return Response('Parameters uri and path mutually exclusive', status=412)
    elif not uri or path:
        uri = uuid4().urn

    if path:
        if '..' in path:
            return Response('\'..\' not allowed in path', 412)

        path = safe_join(ROOT, 'path/' + path)
    else:
        path = safe_join(ROOT, 'hash/' + get_path(uri))

    archive(path, request.stream, uri=uri, expected_hash=hash)

    return 'OK'


@app.route('/retrieve', methods=[ 'GET' ])
def retrieve():
    uri = request.args.get('uri', None)
    path = request.args.get('path', None)
    hash = request.args.get('hash', None)

    if uri and path:
        return Response('Parameters uri and path mutually exclusive\n', status=412)
    
    if path:
        if '..' in path:
            return Response('\'..\' not allowed in path', 412)

        path = safe_join(ROOT, 'path/' + path)
    else:
        path = safe_join(ROOT, 'hash/' + get_path(uri))

    if not isfile(path):
        return Response('No such file\n', status=412)

    return send_file(path)


def archive(path, stream, uri=None, expected_hash=None):
    data = ' '
    hash = md5()

    # actually DO checksum checking

    if not isdir(dirname(path)):
        makedirs(dirname(path))

    with open(path, 'w') as f:
        while data != '':
            data = stream.read(1024)
            hash.update(data)
            f.write(data)

    if uri:
        _log('STORED object with uri %s at %s, md5:%s' % (uri, path, hash.hexdigest()))
    else:
        _log('STORED object at %s, md5:%s' % (path, hash.hexdigest()))


def get_path(uri):
    hex = md5(uri).hexdigest()
    s = [ hex[ 2*i:2*i+2 ] for i in range(0,4) ] + [ hex ]
    
    return '/'.join(s)


def _log(message, t=datetime.utcnow()):
    with open("%s/log" % ROOT, 'a') as logfile:
        logfile.write(t.isoformat() + ' ' + message + '\n')


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-t', '--temp_directory', default='/tmp')
    parser.add_argument('-p', '--port', type=int, default=8080)
    parser.add_argument('archive')
    args = vars(parser.parse_args())
    ROOT = abspath(args['archive'])
    TMP=abspath(args['temp_directory'])

    app.run(host='0.0.0.0', port=args['port'], threaded=True)

