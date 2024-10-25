from dataclasses import dataclass

@dataclass
class PIDController:
    Kp: float
    Ki: float
    Kd: float
    integral: float = 0.0
    previous_error: float = 0.0

    def update(self, measurement: float, target: float, dt: float) -> float:
        """
        Calculate PID output value for given reference input and feedback.

        :param measurement: The current measured value.
        :param target: The desired setpoint at the current time step.
        :param dt: Time interval.
        :return: Control variable.
        """
        error = target - measurement
        self.integral += error * dt
        derivative = (error - self.previous_error) / dt if dt > 0 else 0.0 

        output = self.Kp * error + self.Ki * self.integral + self.Kd * derivative 

        self.previous_error = error

        return output

