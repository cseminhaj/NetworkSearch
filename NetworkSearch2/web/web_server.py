from NetworkSearch2.interface.unifiedInterface import interface

import os
import sys
import platform
import json
import time
from datetime import datetime
from string import Template
import bottle
from bottle import response, request, static_file
import logging

#SERVER = platform.uname()[1]
#CLOUD_SEARCH_SYSTEM_PATH = os.path.abspath(os.path.dirname(__file__) + '..')
#PATH = os.path.abspath(os.path.dirname(__file__)) + '/web'
JSON_DATE_HANDLER = lambda obj: obj.isoformat() if isinstance(obj, datetime) else obj

start = datetime.now()


def getResponse(obj):
	"""Creates a JSON object from a Python object""" 
	return json.dumps(obj, default=JSON_DATE_HANDLER)

app = bottle.app()

# the decorator
def enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        # set CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
        if bottle.request.method != 'OPTIONS':
            # actual request; reply with the actual response
            return fn(*args, **kwargs)
    return _enable_cors

@app.route('/search', method=['OPTIONS', 'POST'])
@enable_cors
def seach():
	query = request.json.get('query', None)
	param = request.json.get('parameters', None)
	response.headers['Content-type'] = 'application/json'

	if query and param:
		t0 = time.time()
		payload = {'query': query}
		parameters = dict({'rank':None, 'returnRank':True}.items() + param.items())
		parameters['hop'] = int(parameters['hop'])
        cs = interface(query, parameters)
        cs.search()
        payload['time'] = cs.time			
		
        payload['num_results'] = cs.numResults
        display_lines = list()
        payload['results'] = cs.results
        payload['mongo'] = cs.dbQuery
        payload['parameters'] = cs.parameters   
        payload['mq'] = cs.mq
        payload['vicinity-param'] = cs.vicinity_param
        return getResponse(payload)

@app.route('/easy-search', method=['OPTIONS', 'GET'])
@enable_cors
def eassy_seach():
	query = request.GET.get('q', '').strip()
	response.headers['Content-type'] = 'application/json'

	if query:
		t0 = time.time()
		#print query
		payload = {'query': query}
        parameters = {'rank':None, 'returnRank':True, 'limit':100 , 'isApprox':True, 'tf':5,'nr':5,'tr':5,'hop':10, 'ms':5}
		
		cs = interface(query, parameters)
		cs.search()
		payload['time'] = cs.time			
		
		payload['num_results'] = cs.numResults
		display_lines = list()
		payload['results'] = cs.results
		payload['mongo'] = cs.dbQuery
		payload['parameters'] = cs.parameters   
		payload['mq'] = cs.mq
		payload['vicinity-param'] = cs.vicinity_param
		return getResponse(payload)
	else:
		return None

#static files
@app.route('/')
def index():
    return static_file('index.html', root='/opt/NetworkSearch/NetworkSearch2/web/static')

# Static Routes
@app.route('/sample-query', method=['GET', 'POST'])
@enable_cors
def sample_query():
    return static_file('sample_query.json', root='/opt/NetworkSearch/NetworkSearch2/web/static/etc')

@app.get('/<filename:re:.*\.js>')
def javascripts(filename):
    return static_file(filename, root='/opt/NetworkSearch/NetworkSearch2/web/static/js')

@app.get('/<filename:re:.*\.css>')
def stylesheets(filename):
    return static_file(filename, root='/opt/NetworkSearch/NetworkSearch2/web/static/css')

@app.get('/<filename:re:.*\.(jpg|png|gif|ico)>')
def images(filename):
    return static_file(filename, root='/opt/NetworkSearch/NetworkSearch2/web/static/img')

@app.get('/fonts/<filename:re:.*\.(eot|ttf|woff|svg)>')
def fonts1(filename):
    return static_file(filename, root='/opt/NetworkSearch/NetworkSearch2/web/static/fonts')

@app.get('/<filename:re:.*\.(eot|ttf|woff|svg)>')
def fonts2(filename):
    return static_file(filename, root='/opt/NetworkSearch/NetworkSearch2/web/static/fonts')




if __name__ == "__main__":
	# reference to the class
	if len(sys.argv) > 1:
		if sys.argv[1] == 'stop':
			# get processes of web.py
			webps = []
			for p in psutil.process_iter():
				for cmd in p.cmdline:
					if cmd.endswith('web_server.py') and p.pid != os.getpid():
						webps.append(p)
					if cmd.endswith('web_server.py start') and p.pid != os.getpid():
						webps.append(p)
			# If there is, terminate it
			if webps:
				for p in webps:
					print 'Killing: ' + str(p.pid) + '\t'  + ' '.join(p.cmdline)
					p.kill()
					
		elif sys.argv[1] == 'start':
			app.run(host='0.0.0.0', port=8080, debug=True, server='tornado')
		else: 
			print "Usage: web.py {start,stop}"
			
	else: 
		print "Usage: web.py {start,stop}"
