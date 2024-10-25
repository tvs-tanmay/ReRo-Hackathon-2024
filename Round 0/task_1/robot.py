
# TASK 1

# Problem Statement :
# Move the bot in a straight line for 4 meters.
# For the first meter of the line, go at 25% the max speed 
# For the second meter of the line, go at 50% the max speed 
# For the third meter of the line, go at 75% the max speed 
# For the fourth meter of the line, go at 100% the max speed  

# Wheel circumference is 10 cm
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
    

## YOUR CODE HERE ##
def main():
    
    # 1 rotation of the wheel at 200RPM takes 0.3 sec
    # Here it is running for 3 seconds covering 1 meter
    set_speed(200, 200)
    time.sleep(3)
    
    # 2nd meter
   

    # 3rd meter


    # 4th meter


## YOUR CODE HERE ##


if __name__ == "__main__":
    main()
