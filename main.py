import os
import sys
import time
import rospy
import socket
import subprocess
from threading import Thread

import network as nt
import tf_handler as tf
import submap_handler as sm

path = "~/catkin_ws" # TEMP PATH

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
def wait_for_ros(): # Waits for ROS nodes to start before reading from topics
    online = False
    
    while not online:
        if sock.connect_ex(('127.0.0.1', 11311)) == 0:
            online = True
        else:
            time.sleep(1)
        
    time.sleep(5) # BRUTE FORCE SLEEP MAY BREAK IN SOME CASES
            
reset = False # Resets ROS if it receives True value over network tables

ros = subprocess.Popen([". " + path + "/devel/setup.sh && roslaunch gbot_core gbot.launch"], shell=True)
wait_for_ros()
rospy.init_node('node')

try:
    while True:
        if not reset:
            if nt.get_reset():
                ros.kill()
                #ros = subprocess.Popen([". " + path + "/devel/setup.sh && roslaunch gbot_core gbot.launch"], shell=True)
                #wait_for_ros()
                reset = True
        else:
            if not nt.get_reset():
                reset = False
        
        tf.listen()
        sm.listen()
        
except KeyboardInterrupt:
    ros.kill()
    sys.exit()