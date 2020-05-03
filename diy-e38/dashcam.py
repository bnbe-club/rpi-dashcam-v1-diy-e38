import picamera
import os
import psutil
import serial
import pynmea2
import time
import json
import itertools
import RPi.GPIO as GPIO
from picamera import Color

DURATION = 60
SPACE_LIMIT = 80
MAX_FILES = 99999
DELETE_FILES = 10

LED_PIN = 4
SWITCH_PIN = 17
POWER_PIN = 27

folder_root = "/home/pi/"
videos_folder = "videos/"
port = "/dev/serial0"
file_number = 0

def clear_space():
	print('Clearing space...')
	i = 0
	files_deleted = 0
	while i < MAX_FILES:
		del_file_path = folder_root + videos_folder + "video%05d.h264" % i
		i = i + 1
		if os.path.exists(del_file_path):
			print ('Deleting: ' + del_file_path)
			os.remove(del_file_path)
			files_deleted = files_deleted + 1

			if(files_deleted >= DELETE_FILES):
				break
	print('Completed.')

def check_space():
	if(psutil.disk_usage(".").percent > SPACE_LIMIT):
		clear_space()

check_space()

serialPort = serial.Serial(port, baudrate = 9600, timeout = 0.5)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(POWER_PIN, GPIO.OUT)
GPIO.output(POWER_PIN, GPIO.LOW)
GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.LOW)

print('Obtaining file number')

if os.path.isfile('config_dashcam.json'):
	f = open('config_dashcam.json', 'r')
	config_dashcam = json.load(f)
	file_number = config_dashcam['file']['number']
	print('Obtained: ')
    	print(file_number)

else:
	print ('File not found. Creating new with 0...')
	file_number = 0
	config_dashcam = {}
	config_dashcam['file'] = { 'number' : file_number }
	with open('config_dashcam.json', 'w') as f:
		json.dump(config_dashcam, f)
	print('Save complete')

if not os.path.exists(videos_folder):
	os.makedirs(videos_folder)
	print ('Created videos folder.')

with picamera.PiCamera() as camera:
	camera.resolution = (1920,1080)
	camera.framerate = 25

 	while file_number < MAX_FILES:
		file_number = file_number + 1
		file_name = folder_root + videos_folder + "video%05d.h264" % file_number
		config_dashcam = {}
		config_dashcam['file'] = { 'number' : file_number }
        	with open('config_dashcam.json', 'w') as f:
	    		json.dump(config_dashcam, f)

		print('Recording to %s' % file_name)
		timeout = time.time() + DURATION

		camera.start_recording(file_name, quality = 20)
		while(time.time() < timeout):
			gps_str = serialPort.readline()

		      	if gps_str.find('GGA') > 0:
		    	    	msg = pynmea2.parse(gps_str)
        		       	camera.annotate_background = Color('black')
               			camera.annotate_text = "TME:%s LAT:%s %s LON:%s %s ALT:%s %s SAT:%s CPU:%s" % (msg.timestamp, msg.lat, msg.lat_dir, msg.lon, msg.lon_dir, msg.altitude, msg.altitude_units, msg.num_sats, psutil.cpu_percent())

			if GPIO.input(LED_PIN):
				GPIO.output(LED_PIN, GPIO.LOW)
			else:
				GPIO.output(LED_PIN, GPIO.HIGH)

			check_space()

			if(GPIO.input(SWITCH_PIN) == 0):
				print('Shutting down...')
				camera.stop_recording()
				time.sleep(3)
				os.system("sudo shutdown -h now")

			time.sleep(0.02)
		camera.stop_recording()
