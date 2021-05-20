import os
from slack import WebClient
from flask import Flask, request

client_id = os.environ["994543213185.2011844838551"]
client_secret = os.environ["b3e344a394624eb293f88a29b79f6e7b"]
oauth_scope = os.environ["SLACK_SCOPES"]

app = Flask(__name__)