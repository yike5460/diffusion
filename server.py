# flask based web server
from flask import Flask, request, jsonify
from flask_cors import CORS

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


import torch
from diffusers import StableDiffusionPipeline
import argparse

import atexit
import json
import os
import sys
import requests
import base64

def generate_pic(args):
    pipe = StableDiffusionPipeline.from_pretrained(
        "./stable-diffusion-v1-5"
        #revision="fp16",
        #torch_dtype=torch.float16,
    )
    pipe = pipe.to("cuda")
    print(args)
    # receive prompt from args
    if args['prompt'] is not None:
        prompt = args['prompt']

    image = pipe(prompt).images[0]

    # receive output from args
    if args['output'] is not None:
        output = args['output']
    image.save(output)

    # encode image to base64 and return
    with open(output, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        print(encoded_string.decode('utf-8'))
        return encoded_string
    
app = Flask(__name__)
CORS(app)

@app.route('/api', methods=['POST'])
def api():
    # get all input arguments
    args = request.get_json()
    logging.info(args)
    return jsonify({'status': 'ok', 'image': str(generate_pic(args))})

@app.route('/api', methods=['GET'])
def api_get():
    return jsonify({'status': 'ok'})

# daemonize the flask server
def daemonize():
    # fork a child process so the parent can exit
    try:
        pid = os.fork()
        if pid > 0:
            # exit first parent
            sys.exit(0)
    except OSError as e:
        sys.stderr.write('fork #1 failed: %d (%s),n' % (e.errno, e.strerror))
        sys.exit(1)

    # decouple from parent environment
    os.chdir('/')
    os.setsid()
    os.umask(0)

    # do second fork
    try:
        pid = os.fork()
        if pid > 0:
            # exit from second parent
            sys.exit(0)
    except OSError as e:
        sys.stderr.write('fork #2 failed: %d (%s),n' % (e.errno, e.strerror))
        sys.exit(1)

    # redirect standard file descriptors
    sys.stdout.flush()
    sys.stderr.flush()
    si = open('/dev/null', 'r')
    so = open('/dev/null', 'a+')
    se = open('/dev/null', 'a+')
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())
    # write pidfile
    atexit.register(delpid)
    pid = str(os.getpid())
    with open('pid', 'w+') as f:
        f.write(pid + 'n')
    
    # start the server
    app.run(host='stable_diffusion', port=5001, debug=False)

if __name__ == '__main__':
    # daemonize()
    app.run(host='0000000', port=5003, debug=True)
