# Python Cloud Broker
UFSCar Sorocaba 2018/02 - Distributed Systems

- Nathan Eloy
- Victor Watanabe

## Project Setup
Install [Pipenv](https://github.com/pypa/pipenv). Run in project folder `pipenv install`.

## Cloud Broker
Project done in [AWS](https://aws.amazon.com/). Use PuTTY SSH client to connect. Cloud Broker uses NoSQL ([MongoDB](https://mongodb.com/)).

To transfer _cloud-broker.py_ to cloud, use `pscp -i [.ppk PRIVATE KEY LOCATION] src/cloud-broker.py ubuntu@[PUBLIC DNS]:/home/ubuntu/cloud-broker.py`.

## Misc Details
This project represents a minimal RESTful Cloud Broker for Virtual Machines.

Cloud Broker uses `virtual_machines` collection within `provider_data` database.

Both Cloud Broker and Provider must act as HTTP Servers - Cloud Broker for receiving HTTP requests from both Client (VM request) and Provider (VM update), and Provider for receiving HTTP requests from Client (VM usage).
