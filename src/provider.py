# Sistemas Distribuídos - Projeto Cloud Broker
# 
# Nathan Eloy de Miranda    726575
# Victor Hide Watanabe      726591

import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import json
import threading

## GLOBALS ##

RES_ID = 1

## For pretty output
CYAN = "\x1b[1;36m"
BLUE = "\x1b[1;34m"
YELLOW = "\x1b[1;33m"
GREEN = "\x1b[1;32m"
RED = "\x1b[1;31m"
DEFAULT = "\x1b[0m"

## Cloud Broker IP
CB_ADDRESS = "http://localhost:8090"

## CLASSES ##

class RequestHandler(BaseHTTPRequestHandler):
    # POSTs from Client
    def do_POST(self):
        # Parse request body
        rbody = json.loads(self.rfile.read(int(self.headers.get('Content-Length'))))

        # Updates VM status
        ident = int(rbody["id"])
        PROVIDER.updateClient(ident, self.client_address[0])

        print(f'\n{CYAN}[i]{DEFAULT} Recurso de ID {ident} atribuído ao cliente {self.client_address[0]}')

        # Reply
        self.send_response(204)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
    # DELETEs from Client
    def do_DELETE(self):
        # Parse request body
        rbody = json.loads(self.rfile.read(int(self.headers.get('Content-Length'))))

        # Updates VM status
        ident = int(rbody["id"])
        PROVIDER.updateClient(ident, None)

        print(f'\n{CYAN}[i]{DEFAULT} Recurso de ID {ident} liberado')

        # Reply
        self.send_response(204)
        self.send_header('Content-type', 'application/json')
        self.end_headers()


class Resource:
    def __init__(self, int_ID, int_CPU, float_RAM, float_HDD, float_price_hour):
        self.ID = int_ID
        self.CPU = int_CPU
        self.RAM = float_RAM
        self.HDD = float_HDD
        self.price = float_price_hour
        self.client = None

    def setClient(self, client_IP):
        self.client = client_IP

    def hasClient(self):
        return True if self.client != None else False

class Provider():
    def __init__(self, port):
        self.port = port
        self.resources = []

    # Prints signed VMs
    def printResources(self):
        if len(self.resources) > 0:
            print(f'\n{CYAN}[i]{DEFAULT} Recursos cadastrados:')

            # Formatting and printing
            print(f'{CYAN}#\tCliente                  \tID \tvCPUs     \tRAM (GBs) \tHDD (GBs) \tPreço/Hora (R$)')
            for i,r in enumerate(self.resources):
                vmid = r.ID
                client = fillString(str(r.client), 25)
                CPU = fillString(str(r.CPU), 10)
                RAM = fillString(str(r.RAM), 10)
                HDD = fillString(str(r.HDD), 10)
                price = r.price

                print(f'{CYAN}{i}{DEFAULT}\t{client}\t{vmid}\t{CPU}\t{RAM}\t{HDD}\t{price}')
        else:
            print(f'{YELLOW}[!]{DEFAULT} Nenhum recurso está cadastrado no momento')

    # Updates a resource status
    def updateClient(self, resource_id, client_IP):
        for r in self.resources:
            if r.ID == resource_id:
                # Updates CB
                params = {'port' : self.port, 'id' : str(r.ID), 'cpu' : str(r.CPU), 'ram' : str(r.RAM), 'hdd' : str(r.HDD), 'price' : str(r.price), 'client': str(client_IP)}

                response = requests.put(CB_ADDRESS, json=params)

                # 204: success, no content
                if response.status_code == 204:
                    print(f'{GREEN}[✓]{DEFAULT} Recurso #{r.ID} atualizado')
                else:
                    print(f'{RED}[X]{DEFAULT} Erro {response.status_code}')
                    break

                r.setClient(client_IP)
                return

    # Register new resource
    def registerResource(self, int_amount, int_CPU, float_RAM, float_HDD, float_price):
        global RES_ID

        for _ in range(int_amount):
            resource = Resource(RES_ID, int_CPU, float_RAM, float_HDD, float_price)
            self.resources.append(resource)

            params = {'port' : self.port, 'id' : str(resource.ID), 'cpu' : str(resource.CPU), 'ram' : str(resource.RAM), 'hdd' : str(resource.HDD), 'price' : str(resource.price), 'client': None}
            response = requests.put(CB_ADDRESS, json=params)

            # 204: success, no content
            if response.status_code == 204:
                print(f'{GREEN}[✓]{DEFAULT} Recurso #{resource.ID} criado')
            else:
                print(f'{RED}[X]{DEFAULT} Erro {response.status_code}')
                break

            RES_ID += 1

    # Removes a resource
    def removeResource(self, resource_index):
        if resource_index >= 0 and resource_index < len(self.resources):
            if not self.resources[resource_index].hasClient():
                resource_id = self.resources[resource_index].ID

                params = {'port' : self.port, 'id' : resource_id}
                response = requests.delete(CB_ADDRESS, json=params)

                # 204: success, no content
                if response.status_code == 204:
                    self.resources.pop(resource_index)
                    print(f'{GREEN}[✓]{DEFAULT} Recurso #{resource_index} removido')
                else:
                    print(f'{RED}[X]{DEFAULT} Erro {response.status_code}')
            else:
                print(f'{YELLOW}[!]{DEFAULT} Recurso #{resource_index} está sendo utilizado por um cliente')
        else:
            print(f'{YELLOW}[!]{DEFAULT} O recurso desejado não existe')


## METHODS ##

def fillString(string, size):
    if string != None and len(string) > size:
        string = string[:size - 3] + ".."
    elif string != None and len(string) < size:
        string = string + (' ' * (size - len(string)))
    return string

def isFloat(var):
    try:
        float(var)
        return True
    except (ValueError, TypeError):
        return False

def isInt(var):
    try:
        int(var)
        return True
    except (ValueError, TypeError):
        return False

def serverThread(port, server_class=HTTPServer, handler_class=RequestHandler):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

    print(f'Servidor HTTP iniciando na porta {port}')
    httpd.serve_forever()

def run():
    global PROVIDER
    print(f'{CYAN}[i]{DEFAULT} Inicializando provedor')
    
    port = None
    while not isInt(port) or int(port) < 8050 or int(port) > 8060:
        port = input(f'{CYAN}[i]{DEFAULT} Insira a porta do provedor (de 8050 a 8060)\n> ')
    port = int(port)

    PROVIDER = Provider(port)

    # Calls request handler thread
    threading.Thread(target=serverThread, args=[port], daemon=True).start()

    # Receives input
    while True:
        command = input(f'\n{CYAN}[i]{DEFAULT} Insira um comando válido [register, remove, print], exit]\n> ')

        if command.find('register') == 0:
            int_amount = None
            int_CPU = None
            float_RAM = None
            float_HDD = None
            float_price = None

            while not isInt(int_amount) or int(int_amount) < 1:
                int_amount = input("Número de máquinas virtuais: ")
            int_amount = int(int_amount)

            while not isInt(int_CPU)  or int(int_CPU) < 1:
                int_CPU = input("Número de CPUs em cada VM: ")
            int_CPU = int(int_CPU)

            while not isFloat(float_RAM) or float(float_RAM) <= 0:
                float_RAM = input("RAM (GB) em cada VM: ")
            float_RAM = float(float_RAM)

            while not isFloat(float_HDD) or float(float_HDD) <= 0:
                float_HDD = input("HDD (GB) em cada VM: ")
            float_HDD = float(float_HDD)

            while not isFloat(float_price) or float(float_price) <= 0:
                float_price = input("Preço (R$) de cada VM: ")
            float_price = float(float_price)

            PROVIDER.registerResource(int_amount, int_CPU, float_RAM, float_HDD, float_price)
        elif command.find('remove') == 0:
            if len(PROVIDER.resources) > 0:
                PROVIDER.printResources()

                index = None
                while not isInt(index):
                    index = input(f'Índice do recurso a ser removido:\n> ')
                index = int(index)

                PROVIDER.removeResource(index)
            else:
                print(f'{YELLOW}[!]{DEFAULT} Nenhum recurso está cadastrado no momento')
        elif command.find('print') == 0:
            PROVIDER.printResources()
        elif command.find('exit') == 0:
            print(f'{CYAN}[i]{DEFAULT} Finalizando provedor. Tchau')
            break

if __name__ == "__main__":
    run()