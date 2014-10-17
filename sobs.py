#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import (Flask, render_template, request, make_response, Response, abort, send_file, redirect, url_for)
from argparse import ArgumentParser
from uuid import uuid4
from os.path import abspath,dirname,basename,join,isfile,isdir
from os import makedirs
from hashlib import md5

app = Flask(__name__)
app.debug = True
ROOT=None

@app.route('/store', methods=[ 'PUT' ])
def store():
    if 'uri' in request.args and 'path' in request.args:
        abort(412)

    uri = request.args.get('uri', uuid4().urn)
    path = request.args.get('path', get_path(uri))
    hash = request.args.get('hash', None)

    archive(path, request.stream, expected_hash=hash)

    return uri

@app.route('/retrieve', methods=[ 'GET' ])
def retrieve():
    path = get_path(request.args.get('uri'))

    if not isfile(path):
        abort(404)

    return send_file(path)

def archive(uri, stream, expected_hash=None):
    path = get_path(uri)
    data = ' '
    hash = md5()

    if not isdir(dirname(path)):
        makedirs(dirname(path))

    with open(path, 'w') as f:
        while data != '':
            data = stream.read(1024)
            hash.update(data)
            f.write(data)

def get_path(uri):
    if uri.startswith('urn:uuid'):
        s = [ 'urn', 'uuid' ] + [ uri[9:][ 2*i:2*i+2 ] for i in range(0,4) ] + [ uri ]
    elif uri.startswith('urn:nbn'):
        hex = md5(uri).hexdigest()
        s = [ 'urn', 'nbn' ] + [ hex[ 2*i:2*i+2 ] for i in range(0,4) ] + [ hex ]
    elif uri.startswith('http') or uri.startswith('https'):
        s = [ x for x in split(':|/|-', uri) if x != '' ]
    else:
        hex = md5(uri).hexdigest()
        s = [ 'md5' ] + [ hex[ 2*i:2*i+2 ] for i in range(0,4) ] + [ hex ] 
    
    return '/'.join([ ROOT ] + s)

def _log(message, t=datetime.utcnow()):
    with open("%s-log" % self.url[7:], 'a') as logfile:
        logfile.write(t.isoformat() + ' ' + message + '\n')

if __name__ == "__main__":
    parser = ArgumentParser()
    #parser.add_argument('-p', '--path_scheme', default='hash')
    parser.add_argument('-p', '--port', type=int, default=8080)
    parser.add_argument('archive')
    args = vars(parser.parse_args())
    ROOT = abspath(args['archive'])

    app.run(host='0.0.0.0', port=args['port'], threaded=True)

