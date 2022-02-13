import os
import time
import rospy
import signal
import socket
import subprocess
from networktables import NetworkTables

import var


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def ros_start(): # Waits for ROS nodes to start before reading from topics
    ros = subprocess.Popen(["/bin/bash", "launch.sh"])
    online = False
    
    while not online:
        if sock.connect_ex(('127.0.0.1', 11311)) == 0:
            online = True
        else:
            time.sleep(1)
        
    time.sleep(5) # BRUTE FORCE SLEEP MAY BREAK IN SOME CASES
    return ros
 
    
def proc_start():
    tf_proc = subprocess.Popen(['python', 'tf_handler.py'])
    sm_proc = subprocess.Popen(['python', 'submap_handler.py'])
    
    return tf_proc, sm_proc


NetworkTables.initialize(server=var.ip)
table = NetworkTables.getTable("lidar")

def get_reset():
    reset = table.getBoolean("reset", False)
    return reset
 
   
reset = False # Resets ROS if it receives True value over network tables

ros = ros_start()
tf_proc, sm_proc = proc_start()

while True:
    if not reset:
        if get_reset():
            os.kill(ros.pid, signal.SIGTERM)
            ros.wait()
            
            tf_proc.terminate()
            sm_proc.terminate()
            tf_proc.wait()
            sm_proc.wait()
            
            ros = ros_start()
            tf_proc, sm_proc = proc_start()
            
            reset = True
    else:
        if not get_reset():
            reset = False