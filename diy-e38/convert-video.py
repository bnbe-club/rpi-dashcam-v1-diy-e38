
import os

START_INDEX = 28
END_INDEX = 40

print("Starting conversion...")
if START_INDEX > END_INDEX:
	print("Error! Check index values")
else:
	if not os.path.exists("output/"):
		os.makedirs("output/")
		print("Created output folder.")

	i=START_INDEX
	while(i <= END_INDEX):
		input_file =  "videos/video%05d.h264" % i
		output_file = "output/video%05d.mp4" % i
		i = i + 1

		if os.path.exists(input_file):
			print("Converting: " + input_file)
			conversion_command = "MP4Box -add " + input_file + " " + output_file
			print conversion_command
			os.system(conversion_command)
	print("Conversion complete.")
