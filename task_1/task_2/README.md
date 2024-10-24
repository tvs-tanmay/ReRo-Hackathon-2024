# ReRo Hackathon

## Problem Statement: Coffee Roasting Temperature Control Using PID Controller

### Objective:
Simulate a coffee roasting process to control the bean temperature using a PID (Proportional-Integral-Derivative) controller. The goal is to maintain a precise temperature profile over time to ensure optimal coffee roasting, targeting specific roast milestones. Participants need to implement the roasting system in Python and tune the PID parameters to closely follow a target temperature curve.

![c24860bd-7a2e-464b-a99d-c2ee84ac40f2](https://github.com/user-attachments/assets/900adaf5-20ba-446d-96fb-c7233a48f5bb)

**PID Equation**

```
output= Kp*error +Iterm + Kd*(error - previous error)$
```

### Steps to follow:

1. **Navigate to the Task Directory**
   - Go to the `task_1` folder where the files `sim.py` and `pid_controller.py` are located.

   ```bash
   cd path/to/task_1
   
2. **Edit the PID Controller**
   - Open the `sim.py` file in your preferred editor to implement or adjust the PID controller and save the file.
   - Inside the `sim.py` file, define the PID controller parameters (`Kp`, `Ki`, `Kd`) and implement the control logic in the given function. Make sure to adjust the parameters to achieve stable control of the temperature.
   - ## **dont make any changes to the sim.py except the (`Kp`, `Ki`, `Kd`)**
   ```code-block
   pid = PIDController(
   Kp=0.0,    # Increased Proportional gain for better responsiveness
   Ki=0.0,   # Decreased Integral gain to reduce overshoot
   Kd=0.0     # Increased Derivative gain to dampen oscillations)

3. **Test the PID Controller**
   - Run the `sim.py` file to simulate the roasting process and check the performance of your PID controller. The script will generate output showing the temperature profile and whether it meets the desired curve

   ```bash
   python sim.py

4. **Submit Your Solution**
   - Once you are confident in your PID controller implementation, take screenshots of your plot and copy your `Kp`,`Kd` and `Ki` values in a text file in a folder with your team name and upload the folder to your google drive and send the link of the drive (make sure it is public)

   ```folder structure
   .└── <TEAM_NAME>/
      ├── pid_values.txt
      └── screenshots(folder)/
          └── .png

