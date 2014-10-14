#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import (Flask, render_template, request, make_response, Response, abort, send_file, redirect, url_for)
from argparse import ArgumentParser
from uuid import uuid4
from os.path import abspath,dirname,basename,join,isfile,isdir
from os import makedirs
from hashlib import md5

app = Flask(__name__)
app.debug = False
ROOT=None

@app.route('/store', methods=[ 'POST', 'PUT' ])
def store():
    uri = request.args.get('uri') if 'uri' in request.args else uuid4().urn
    archive(request.stream, get_path(uri))

    return uri

@app.route('/retrieve', methods=[ 'GET' ])
def retrieve():
    path = get_path(request.args.get('uri'))

    if not isfile(path):
        abort(404)

    return send_file(path)

def archive(stream, path):
    data = ' '

    if not isdir(dirname(path)):
        makedirs(dirname(path))

    with open(path, 'w') as f:
        while data != '':
            data = stream.read(1024)
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


if __name__ == "__main__":
    parser = ArgumentParser()
    #parser.add_argument('-p', '--path_scheme', default='hash')
    parser.add_argument('archive')
    args = vars(parser.parse_args())
    ROOT = abspath(args['archive'])

    app.run(host='0.0.0.0', port=8080, threaded=True)

