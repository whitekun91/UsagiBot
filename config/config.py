import json

with open('config/config.json', 'r') as f:
    json_config = json.load(f)

token = json_config['token']
