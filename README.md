# Web Scanner Honeypot

This is a python implementation of the technical task for Paymark.

All sources are in the `src` folder.

## How to use :

### With docker-compose
Run `docker-compose up --scale worker=4` to set up the stack.  
The stack is composed of the honeypot, a Locust master, and n Locust worker (4 in the command above).

The honeypot uses the stock Python 3.9 Alpine image, without anything added.  
[Locust](https://locust.io/) is an open-source load testing tool used to stress test the honeypot.

Go to [localhost:8089](http://localhost:8089) to launch the stress test of the honeypot.  
If everything is working correctly and after ~30 seconds (with the default values for the number of users and spawn rate), Locust should output `All users spawned` in the docker logs.  
On the locust interface, RPS should be a 0, because the honeypot is preventing all users from Locust to *load* the page.

### Locally
Python 3.9 is required to run directly on your computer with `python -u src/main.py -a localhost -p 8080`.


## How it works

The Honeypot creates a simple TCP socket listening to the asked `ip:port`.

On client connexion, headers are read to define if it's a **GET** request or anything else. Only GET requests are processed.  
After validation, headers forcing the bot to establish a chunked transfer are sent followed by an infinite stream of *Not Found*, every 5 seconds.  

To prevent the main thread to be stuck, each connection is managed by a new process with `multiprocessing.Process`. With this method, the honeypot is capable of managing multiple connexions without stalling.  
The only limiting factor can be the CPU if a bot manages to create hundreds of connexion per second or ram if the honeypot needs to manage a huge number of connexions for a long time.