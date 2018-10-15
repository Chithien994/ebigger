import threading
import time
import os
from random import randint
start_time = time.time()
class myThread (threading.Thread):
   def __init__(self, threadID):
      threading.Thread.__init__(self)
      self.threadID = threadID
   def run(self):
      print_time()



def print_time():
	elapsed_time = time.time() - start_time
	print("Time: %.0fs"%elapsed_time)

# Create new threads
# thread1 = myThread(1, "Thread-1", 1)

# # Start new Threads
# thread1.start()
count = 0
key = 0
for x in range(1,100000000000000000):
	count+= 1
	rd = randint(100000000000000000000000000000000000000000, 999999999999999999999999999999999999999999)
	if "77777" in str(rd) or "00000" in str(rd) or "11111" in str(rd) or "22222" in str(rd) or "33333" in str(rd) or "44444" in str(rd) or "55555" in str(rd) or "66666" in str(rd) or "88888" in str(rd) or "99999" in str(rd):
		key+= 1
	print(rd)
	print("count: ",count)
	print("Number Key Success: ",key)
	myThread(1).start()
	os.system('cls')