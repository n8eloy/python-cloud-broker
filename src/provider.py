# Sistemas Distribuídos - Projeto Cloud Broker
# 
# Nathan Eloy de Miranda    726575
# Victor Hide Watanabe      726591

import requests

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
CB_ADDRESS = "http://18.228.156.230:8090"

## CLASSES ##

class Resource:
    def __init__(self, int_ID, int_CPU, float_RAM, float_HDD, float_price_hour):
        self.ID = int_ID
        self.CPU = int_CPU
        self.RAM = float_RAM
        self.HDD = float_HDD
        self.price = float_price_hour

class Provider():
    def __init__(self, port):
        self.port = port
        self.resources = []

    # Prints signed VMs
    def printResources(self):
        if len(self.resources) > 0:
            print(f'\n{CYAN}[i]{DEFAULT} Recursos cadastrados:')

            # Formatting and printing
            print(f'{CYAN}#\tID \tvCPUs     \tRAM (GBs) \tHDD (GBs) \tPreço/Hora (R$)')
            for i,r in enumerate(self.resources):
                vmid = r.ID
                CPU = fillString(str(r.CPU), 10)
                RAM = fillString(str(r.RAM), 10)
                HDD = fillString(str(r.HDD), 10)
                price = r.price

                print(f'{CYAN}{i}{DEFAULT}\t{vmid}\t{CPU}\t{RAM}\t{HDD}\t{price}')
        else:
            print(f'{YELLOW}[!]{DEFAULT} Nenhum recurso está cadastrado no momento')

    # Register new resource
    def registerResource(self, int_amount, int_CPU, float_RAM, float_HDD, float_price):
        global RES_ID

        for _ in range(int_amount):
            resource = Resource(RES_ID, int_CPU, float_RAM, float_HDD, float_price)
            self.resources.append(resource)

            params = {'port' : self.port, 'id' : str(resource.ID), 'cpu' : str(resource.CPU), 'ram' : str(resource.RAM), 'hdd' : str(resource.HDD), 'price' : str(resource.price), 'client': "None"}
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
            resource_id = self.resources[resource_index].ID

            params = {'port' : self.port, 'id' : resource_id}
            response = requests.delete(CB_ADDRESS, json=params)

            # 204: success, no content, 403: forbidden, resource is busy
            if response.status_code == 204:
                self.resources.pop(resource_index)
                print(f'{GREEN}[✓]{DEFAULT} Recurso #{resource_index} removido')
            elif response.status_code == 403:
                print(f'{YELLOW}[!]{DEFAULT} Recurso sendo utilizado')
            else:
                print(f'{RED}[X]{DEFAULT} Erro {response.status_code}')
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

def run():
    global PROVIDER
    print(f'{CYAN}[i]{DEFAULT} Inicializando provedor')
    
    port = None
    while not isInt(port) or int(port) < 8050 or int(port) > 8060:
        port = input(f'{CYAN}[i]{DEFAULT} Insira a porta do provedor (de 8050 a 8060)\n> ')
    port = int(port)

    PROVIDER = Provider(port)

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