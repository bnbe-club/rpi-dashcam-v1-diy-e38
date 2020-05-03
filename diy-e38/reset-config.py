import os
import json

REST_NUMBER = 0

print("Deleting configuration...")


if os.path.isfile('config_dashcam.json'):
	os.remove('config_dashcam.json')

config_dashcam = {}
config_dashcam['file'] = { 'number' : 0 }

with open('config_dashcam.json', 'w') as f:
	json.dump(config_dashcam, f)

print("Completed.")

