#!/bin/bash

cd server
node app.js & cd .. & python3 server.py & cd crossword & npm run dev
echo "*Scraper running*" 
# cd ..
# echo $(pwd)
# python3 server.py
# cd crossword
# npm run dev