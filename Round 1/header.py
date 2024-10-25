import random


def dump(value:str):
    """
    Print the value to the dashboard console, should be used in place of python default print. 
    Can be used for debugging purposes, does not have the default attributes of the python print function

    @param:
        value: str - Value to be printed to the console

    """
    print(value)


def set_right_speed(speed: int):
    """
    Function to set the speed of the motors
    
    @param:
        speed: int - Speed of the right motor 

    @return:
        bool - Speed set success or failure

    speed  should be a number between -100 and 100,
    speed < 0 : moving backwards
    speed = 0 : stop
    speed > 0 : moving forward

    """

    if not (-100 <= speed <= 100):
        return False
    
    print("Right motor running @ speed", speed)
    return True
    

def set_left_speed(speed: int):
    """
    Function to set the speed of the left motor
    
    @param:
        speed: int - Speed of the left motor 

    @return:
        bool - Speed set success or failure

    speed should be a number between -100 and 100,
    speed < 0 : moving backwards
    speed = 0 : stop
    speed > 0 : moving forward

    """

    if not (-100 <= speed <= 100):
        return False
    
    print("Right motor running @ speed", speed)
    return True
    


def get_ir_values():
    """
    Function to get the color values of the sensor array, left to right
    
    @return:
        color: [bool, bool, bool, bool, bool] - Ground color white or black

        white will be represented by a value of True, 
        and black will be represented by the value False

    """

    global color_sensors
    return [int(random.choice([True, False])) for _ in range(5)]


def stop_right():
    """
    Function to stop the right motor
    """

    print("Right motor stopped")


def stop_left():
    """
    Function to stop the left motor
    """

    print("Left motor stopped")
