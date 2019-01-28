# Python Cloud Broker
UFSCar Sorocaba 2018/02 - Distributed Systems

- Nathan Eloy
- Victor Watanabe

## Project Setup
Install [Pipenv](https://github.com/pypa/pipenv). Run in project folder `pipenv install`.

## Cloud Broker
Project originally done in [AWS](https://aws.amazon.com/) Ubuntu Machine, using PuTTY SSH client to connect to Cloud Broker VM. Cloud Broker uses NoSQL ([MongoDB](https://mongodb.com/)) to save JSON documents, using `virtual_machines` collection within `provider_data` database. Cloud Broker acts as the only HTTP Server, intermediating HTTP communications between Clients and Providers.

To transfer _cloud-broker.py_ to cloud, use `pscp -i [.ppk PRIVATE KEY LOCATION] src/cloud-broker.py ubuntu@[PUBLIC DNS]:/home/ubuntu/cloud-broker.py`.

## Misc Details
This project represents a minimal RESTful Cloud Broker for Virtual Machines.
