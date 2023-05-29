# RobotArmGestures
Controlling the Hiwonder xArm1S robotic arm with hand gestures in Python

![Screenshot](https://github.com/James-P-D/RobotArmGestures/blob/main/screenshot.gif)

## Introduction

A very quick (and not totally successful) attempt at using hand gestures to control the off-the-shelf xArm robotic arm.

## Usage

After pluggin in your xArm, the application will continuously display the message `Waiting for single hand..` until your hand is visible from the camera. Once the hand has been detected the message `Stretch hand for X more seconds..` during which time you should stretch your fingers as far and wide as you can. Once the timer has completed the message `Clench hand for X more seconds..` during which you should clench your fist as tightly as possible.

Once this second timer has completed, you will either be told the program was unable to calibrate the measurements and you will have to repeat the process again, or you will be presented with a message stating `Relax hand for X more seconds..` at which point you should rest your fingers at the mid-point between stretch and clench.

You can now  
* Pan hand left and right to rotate the robot arm
* Thumb to open and close pincers
* Index finger  to rotate the pincer
* Middle finger to flex the wrist
* Ring finger to flex the elbow
* Pinkie to flex the shoulder

## Warning

The program works, but make sure you have your xArm on a flat surface and that it is secured. If the suction pads at the base of the robot arm are not secured properly you may find minor movements of your fingers cause the arm to move quickly and topple over!
