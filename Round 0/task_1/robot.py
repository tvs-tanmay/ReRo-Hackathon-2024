
# TASK 1

# Problem Statement :
# Move the bot in a straight line for 4 meters.
# For the first meter of the line, go at 25% the max speed 
# For the second meter of the line, go at 50% the max speed 
# For the third meter of the line, go at 75% the max speed 
# For the fourth meter of the line, go at 100% the max speed  

# Wheel circumference is 10 cm, so the distance covered for one revolution is 10cm.
# Max speed is 800 rpm

# Use no libraries other than that ones imported

import os
import time
import sys

max_speed = 800 

# Set motor speed
def set_speed(right_speed, left_speed):
    
    if abs(right_speed) > max_speed or abs(left_speed) > max_speed:
        return print("Error")
    else:
        return print(right_speed, left_speed)
    
def main(): 

    # 1 rotation of the wheel at 200RPM takes 0.3 sec
    # Here it is running for 3 seconds covering 1 meter
    # 25% of Max Speed = 200
    # 50% of Max Speed = 400
    # 75% of Max Speed = 600
    # 100% of Max Speed = 800
    
    # There are 10 revolutions for every metre travelled.
    # Time taken to travel 1 metre = 3 seconds
    # Time taken to travel 1 metre = 1.5 seconds
    # Time taken to travel 1 metre = 1 second
    # Time taken to travel 1 metre = 0.75 seconds
    
    set_speed(200, 200)
    time.sleep(3)
    
    # 2nd meter
    set_speed(400, 400)
    time.sleep(1.5)

    # 3rd meter
    set_speed(600, 600)
    time.sleep(1)

    # 4th meter
    set_speed(800, 800)
    time.sleep(0.75)

if __name__ == "__main__":
    main()
