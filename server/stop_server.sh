#!/bin/bash

zdaemon -p "python rest_server.py" -d -s zdsock-1 stop
zdaemon -p "python sockjs_server.py" -d -s zdsock-2 stop
