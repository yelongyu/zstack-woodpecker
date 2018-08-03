#!/bin/python
import sys
import traceback
from flask import Flask, jsonify, request, abort, make_response
from flask_restful import reqparse
from uuid import uuid4
from threading import Lock

app = Flask(__name__)
token = None
comment = None
store = dict()
lock = Lock()

@app.route('/test/api/v1.0/store/create', methods=['POST'])
def create_key():
	global store

	parser = reqparse.RequestParser()
	parser.add_argument('key', help='Key')
	parser.add_argument('value', help='Value')

	args = parser.parse_args()
	print args
	if args['key'] == None:
		abort(404)

	store[args['key']] = args['value']
	return make_response(jsonify({"result":"success"}), 201)


@app.route('/test/api/v1.0/store/<string:key>', methods=['GET'])
def query_key(key):
	global store

	if not store.has_key(key):
		abort(404)
	return make_response(jsonify({"result":store[key]}), 200)

@app.route('/test/api/v1.0/tokens/create', methods=['POST'])
def create_token():
	global token
	global comment
	global lock

	with lock:
  		if token != None:
			abort(404)
		token = uuid4()
	parser = reqparse.RequestParser()
	parser.add_argument('comment', help='Comment')

	args = parser.parse_args()
	print args
	print token
	if args['comment'] == None:
		comment = None
	else:
		comment = args['comment']

	return make_response(jsonify({"token":token}), 201)


@app.route('/test/api/v1.0/tokens/<string:token_id>', methods=['DELETE'])
def delete_token(token_id):
	global token
	global comment
	global lock

	with lock:
		if str(token) != str(token_id):
			abort(404)
		token = None
	comment = None
	return make_response(jsonify({'result': 'success'}), 200)


@app.errorhandler(404)
def not_found(error):
	    return make_response(jsonify({'error': 'Not found'}), 404)

def run_server():
        app.config['TEMPLATES_AUTO_RELOAD'] = False
	app.run(host="0.0.0.0", port="8888", debug=True)

if __name__ == '__main__':
        app.config['TEMPLATES_AUTO_RELOAD'] = False
	app.run(host="0.0.0.0", port="8888", debug=True)
