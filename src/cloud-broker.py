# Sistemas Distribuídos - Projeto Cloud Broker
# 
# Nathan Eloy de Miranda    726575
# Victor Hide Watanabe      726591

from pymongo import MongoClient
from http.server import BaseHTTPRequestHandler, HTTPServer
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
        CPU = int(rbody["cpu"])
        RAM = float(rbody["ram"])
        HDD = float(rbody["hdd"])

        # Query for VMs
        query = VM_COLL.find({"client":"None","cpu":{"$gte": CPU},"ram":{"$gte": RAM},"hdd":{"$gte": HDD}}, {'_id': False}).sort("price",1)
        
        # Not enough VMs
        if query.count() < amount:
            print(f'{RED}Não existem VMs o suficiente para o pedido{DEFAULT}')
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
    # POSTs from Client
    def do_POST(self):
        # Parse request body
        rbody = json.loads(self.rfile.read(int(self.headers.get('Content-Length'))))

        opt = str(rbody["opt"])
        client = str(self.client_address[0])
        ident = int(rbody["id"])
        provider = str(rbody["provider"])

        if opt == "add":
            # Updates VM
            result = VM_COLL.update_one({"provider":provider,"id":ident},{"$set": {"client":client}},upsert=False)

            if (result.modified_count > 0):
                print(f'\n{GREEN}Recurso do provedor {provider} de ID {ident} atribuído ao cliente {client}{DEFAULT}')

                # Reply
                self.send_response(204)
                self.end_headers()
            else:
                # Not found
                self.send_response(404)
                self.end_headers()
        elif opt == "del":
            # Updates VM
            result = VM_COLL.update_one({"provider":provider,"id":ident},{"$set": {"client":None}},upsert=False)

            if (result.modified_count > 0):
                print(f'\n{GREEN}Recurso do provedor {provider} de ID {ident} liberado do cliente {client}{DEFAULT}')

                # Reply
                self.send_response(204)
                self.end_headers()
            else:
                # Not found
                self.send_response(404)
                self.end_headers()

    # PUTs from Provider
    def do_PUT(self):
        # Parse request body
        rbody = json.loads(self.rfile.read(int(self.headers.get('Content-Length'))))

        print(f'\n"{self.client_address}" está adicionando ou atualizando {rbody}')
        
        ident = int(rbody["id"])
        CPU = int(rbody["cpu"])
        RAM = float(rbody["ram"])
        HDD = float(rbody["hdd"])
        price = float(rbody["price"])
        provider_server_port = str(rbody["port"])
        provider = "http://"+str(self.client_address[0])+":"+provider_server_port
        client = str(rbody["client"])

        # Add or update VM
        VM_COLL.update_one({"provider":provider,"id":ident},{"$set": {"id":ident, "cpu":CPU, "ram":RAM, "hdd":HDD, "price":price, "provider":provider, "client":client}},upsert=True)

        print(f'{BLUE}Máquinas registradas{DEFAULT}')

        # Reply
        self.send_response(204)
        self.end_headers()
        return
    # DELETEs from Provider
    def do_DELETE(self):
        # Parse request body
        rbody = json.loads(self.rfile.read(int(self.headers.get('Content-Length'))))

        print(f'\n"{self.client_address}" está removendo {rbody}')
        
        ident = int(rbody["id"])
        provider_server_port = str(rbody["port"])
        provider = "http://"+str(self.client_address[0])+":"+provider_server_port

        # Find and remove VM
        if VM_COLL.delete_one({"provider" : provider, "id" : ident, "client" : "None"}).deleted_count > 0:
            print(f'{BLUE}Máquinas removidas{DEFAULT}')

            # Reply
            self.send_response(204)
        elif VM_COLL.find({"provider" : provider, "id" : ident}).count() > 0:
            print(f'{RED}Remoção negada: recursos em uso{DEFAULT}')
            # Resource is being used
            self.send_response(403)
        else:
            # Not found
            self.send_response(404)
        self.end_headers()
        return

## METHODS ##

def run(server_class=HTTPServer, handler_class=RequestHandler):
    server_address = ('', PORT)
    httpd = server_class(server_address, handler_class)

    print(f'Servidor HTTP iniciando na porta {PORT}')
    httpd.serve_forever()

if __name__ == "__main__":
    run()