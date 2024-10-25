from dataclasses import dataclass
# -------------------------------
# PID Controller Implementation
# -------------------------------

@dataclass
class PIDController:
    Kp: float
    Ki: float
    Kd: float
    # Remove the static setpoint
    integral: float = 0.0
    previous_error: float = 0.0

    def update(self, measurement: float, target: float, dt: float) -> float:
        """
        Calculate PID output value for given reference input and feedback.

        :param measurement: The current measured value.
        :param setpoint: The desired setpoint at the current time step.
        :param dt: Time interval.
        :return: Control variable.
        """
        ## YOUR CODE STARTS HERE ##
        error = 
        self.integral += 
        derivative = (error - self.previous_error) / dt if dt > 0 else 0.0

        output = # Your PID output eqaution here

        self.previous_error = error
        ## YOUR CODE ENDS HERE ##
        return output
