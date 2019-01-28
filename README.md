# Python Cloud Broker
UFSCar Sorocaba 2018/02 - Distributed Systems

- Nathan Eloy
- Victor Watanabe

## Project Setup
Install [Pipenv](https://github.com/pypa/pipenv). Run in project folder `pipenv install`.

## Cloud Broker
Using [AWS](https://aws.amazon.com/). Public IP is `54.233.252.96`. Currently using PuTTY SSH client to connect.

## Misc Details
This project represents a minimal RESTful Cloud Broker for Virtual Machines.

Cloud Broker uses NoSQL ([MongoDB](https://mongodb.com/)).

Both Cloud Broker and Provider must act as HTTP Servers - Cloud Broker for receiving HTTP requests from both Client (VM request) and Provider (VM update), and Provider for receiving HTTP requests from Client (VM usage).