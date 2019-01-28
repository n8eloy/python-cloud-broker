# Sistemas Distribuídos - Projeto Cloud Broker
# 
# Nathan Eloy de Miranda    726575
# Victor Hide Watanabe      726591

from pymongo import MongoClient
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import socketserver
import json

## GLOBALS ##

PORT = 8090
CLIENT = MongoClient('localhost', 27017)
DB = CLIENT.provider_data
VM_COLL = DB.virtual_machines

## For pretty output
CYAN = "\x1b[1;36m"
BLUE = "\x1b[1;34m"
YELLOW = "\x1b[1;33m"
GREEN = "\x1b[1;32m"
RED = "\x1b[1;31m"
DEFAULT = "\x1b[0m"

## CLASSES ##    

class RequestHandler(BaseHTTPRequestHandler):
    # GETs from Client
    def do_GET(self):
        # Parse request body
        rbody = json.loads(self.rfile.read(int(self.headers.get('Content-Length'))))

        print(f'\n"{self.client_address}" está pedindo {rbody}')
        print(f'{BLUE}Buscando matching{DEFAULT}')

        amount = int(rbody["amount"])
        CPU = int(rbody["CPU"])
        RAM = float(rbody["RAM"])
        HDD = float(rbody["HDD"])

        # Query for VMs
        query = VM_COLL.find({"CPU":{"$gte": CPU},"RAM":{"$gte": RAM},"HDD":{"$gte": HDD}}, {'_id': False}).sort("price",1)
        
        # Not enough VMs
        if query.count() < amount:
            print(f'{RED}Não existem VMS o suficiente para o pedido{DEFAULT}')
            self.send_response(404)
            self.end_headers()
            return
        
        print(f'{BLUE}Máquinas encontradas, respondendo{DEFAULT}')
        json_answer = []
        for i in range(amount):
            json_answer.append(query[i])
        print(json_answer)

        # Reply
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(json_answer).encode())
        return
    # PUTs from Provider
    def do_PUT(self):
        return
    # DELETEs from Provider
    def do_DELETE(self):
        return

## METHODS ##

def run(server_class=HTTPServer, handler_class=RequestHandler):
    server_address = ('', PORT)
    httpd = server_class(server_address, handler_class)

    print(f'Servidor HTTP iniciando na porta {PORT}')
    httpd.serve_forever()

if __name__ == "__main__":
    run()