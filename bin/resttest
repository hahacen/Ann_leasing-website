#!/bin/bash
set -Eeuo pipefail
set -x

# Log in
http \
  --session=./session.json \
  --form POST \
  "http://localhost:8000/accounts/" \
  username=awdeorio \
  password=password \
  operation=login

# REST API request
http \
  --session=./session.json \
  "http://localhost:8000/api/v1/posts/1/"
