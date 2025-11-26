#!/bin/bash
API_KEY="AQ.Ab8RN6KS_uU_DlwdMGgK1j1y4kgN4BJObskctlI4ja_yWovSwA"
URL="https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${API_KEY}"

echo "Testing API Key against: $URL"

curl -H 'Content-Type: application/json' \
     -d '{ "contents":[{ "parts":[{ "text": "Hello" }] }] }' \
     -X POST ${URL}
