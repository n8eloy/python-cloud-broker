# Sistemas Distribuídos - Projeto Cloud Broker
# 
# Nathan Eloy de Miranda    726575
# Victor Hide Watanabe      726591

import requests
import textwrap

## GLOBALS ##

## For pretty output
CYAN = "\x1b[1;36m"
BLUE = "\x1b[1;34m"
YELLOW = "\x1b[1;33m"
GREEN = "\x1b[1;32m"
RED = "\x1b[1;31m"
DEFAULT = "\x1b[0m"

## Cloud Broker IP
CB_ADDRESS = "http://localhost:8089"

## CLASSES ##

class Resource:
    def __init__(self, int_ID, int_CPU, float_RAM, float_HDD, float_price_hour, provider_IP):
        self.ID = int_ID
        self.CPU = int_CPU
        self.RAM = float_RAM
        self.HDD = float_HDD
        self.price = float_price_hour
        self.provider = provider_IP

class Client:
    def __init__(self):
        self.resources = []

    # Prints VMs in use
    def printResources(self):
        if len(self.resources) > 0:
            print(f'\n{CYAN}[i]{DEFAULT} Recursos sendo usados:')

            # Formatting and printing
            print(f'{CYAN}#\tProvedor                 \tID \tvCPUs     \tRAM (GBs) \tHDD (GBs) \tPreço/Hora (R$)')
            for i,r in enumerate(self.resources):
                vmid = r.ID
                provider = fillString(r.provider, 25)
                CPU = fillString(r.CPU, 10)
                RAM = fillString(r.RAM, 10)
                HDD = fillString(r.HDD, 10)
                price = r.price

                print(f'{CYAN}{i}{DEFAULT}\t{provider}\t{vmid}\t{CPU}\t{RAM}\t{HDD}\t{price}')
        else:
            print(f'{YELLOW}[!]{DEFAULT} Nenhum recurso está sendo usado no momento')

    # For using virtual machines
    def useResource(self, json_resource):
        # Creates resource object
        resource = Resource(json_resource['id'], json_resource['CPU'], json_resource['RAM'], json_resource['HDD'], json_resource['price'], json_resource['provider'])
        print(f'{BLUE}[R]{DEFAULT} Conectando ao provedor para utilizar recurso')

        # Sends VM ID to provider
        params = {'ID':resource.ID}
        
        # We're using a POST since the client is sending his information to the provider
        response = requests.put(resource.provider, params=params)

        # 204: success, no content
        if response.status_code == 204:
            print(f'{GREEN}[✓]{DEFAULT} Provedor conectado, recurso será utilizado')
            self.resources.append(resource)
        else:
            # Unkown
            print(f'{RED}[X]{DEFAULT} Erro {response.status_code}')


    # Stop using virtual machine
    def releaseResource(self, resource_index):
        if resource_index >= 0 and resource_index < len(self.resources):
            # Sends VM ID to provider
            params = {'ID':self.resources[resource_index].ID}
            # We're using a DELETE since the client is removing his bond with the provider
            response = requests.delete(self.resources[resource_index].provider, params=params)
            
            # 204: success, no content
            if response.status_code == 204:
                self.resources.pop(resource_index)
                print(f'Recurso #{resource_index} liberado')
            else:
                # Unkown
                print(f'{RED}[X]{DEFAULT} Erro {response.status_code}')
        else:
            print(f'{YELLOW}[!]{DEFAULT} O recurso desejado não existe')

    # For requesting virtual machines
    def requestResource(self, int_CPU, float_RAM, float_HDD, float_price_hour):
        # Params for GET 
        params = {'CPU' : str(int_CPU), 'RAM' : str(float_RAM) , 'HDD' : str(float_HDD) , 'price' : str(float_price_hour)}
        response = requests.get(CB_ADDRESS, params=params)

        # 200: OK, 404: not found, 5XX: server error
        if response.status_code == 200:
            # Found matching provider
            print(f'{GREEN}[✓]{DEFAULT} Máquinas encontradas:')

            json_data = response.json()

            # Print found VMs
            # Formatting and printing
            print(f'{CYAN}#\tProvedor                 \tID \tvCPUs     \tRAM (GBs) \tHDD (GBs) \tPreço/Hora (R$)')
            for i,r in enumerate(json_data):
                vmid = r["id"]
                provider = fillString(r["provider"], 25)
                CPU = fillString(r["CPU"], 10)
                RAM = fillString(r["RAM"], 10)
                HDD = fillString(r["HDD"], 10)
                price = r["price"]

                print(f'{CYAN}{i}{DEFAULT}\t{provider}\t{vmid}\t{CPU}\t{RAM}\t{HDD}\t{price}')

            command = None
            while command == None or (command.lower() != 's' and command.lower() != 'n'):
                command = input(f'Usar as máquinas virtuais encontradas? (S/N)\n> ')
            
            if command.lower() == 's':
                # Uses resources
                for r in json_data:
                    self.useResource(r)
        elif response.status_code == 404:
            # No match found
            print(f'{YELLOW}[!]{DEFAULT} Não foram econtradas máquinas virtuais para atender à demanda')
        elif response.status_code >= 500 and response.status_code <= 599:
            # Server error
            print(f'{RED}[X]{DEFAULT} Erro interno')
        else:
            # Unkown
            print(f'{RED}[X]{DEFAULT} Erro {response.status_code}')

### FUNCTIONS ###

def fillString(string, size):
    if len(string) > size:
        string = string[:size - 3] + ".."
    elif len(string) < size:
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
    print(f'{CYAN}[i]{DEFAULT} Inicializando cliente')
    client = Client()

    # Receives input
    while True:
        command = input(f'\n{CYAN}[i]{DEFAULT} Insira um comando válido [request, print, stop, exit]\n> ')

        if command.find('request') == 0:
            int_CPU = None
            float_RAM = None
            float_HDD = None
            float_price_hour = None

            while not isInt(int_CPU):
                int_CPU = input("Número de CPUs: ")
            int_CPU = int(int_CPU)

            while not isFloat(float_RAM):
                float_RAM = input("RAM (em GB): ")
            float_RAM = float(float_RAM)

            while not isFloat(float_HDD):
                float_HDD = input("HDD (em GB): ")
            float_HDD = float(float_HDD)

            while not isFloat(float_price_hour):
                float_price_hour = input("Preço de uso por hora: ")
            float_price_hour = float(float_price_hour)

            client.requestResource(int_CPU, float_RAM, float_HDD, float_price_hour)
        elif command.find('stop') == 0:
            if len(client.resources) > 0:
                client.printResources()

                index = None
                while not isInt(index):
                    index = input(f'Índice do recurso a ser liberado:\n> ')
                index = int(index)

                client.releaseResource(index)
            else:
                print(f'{YELLOW}[!]{DEFAULT} Nenhum recurso está sendo usado no momento')
        elif command.find('print') == 0:
            client.printResources()
        elif command.find('exit') == 0:
            print(f'{CYAN}[i]{DEFAULT} Finalizando cliente. Tchau')
            break

if __name__ == "__main__":
    run()