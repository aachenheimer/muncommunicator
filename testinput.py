from msvcrt import *

while True:
	if kbhit():
		print(ord(getche()))