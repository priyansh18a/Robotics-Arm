import serial
import numpy as np
import time
import cv2
import ObjectDetection as od

#time delay between consecutive angle changes
time_delay = 0

# Serial and Aduino Interaction
usbport = 'COM4'
srl = serial.Serial(usbport, 9600, timeout = 1)

def move(servo, angle):
    if(0 <= angle <= 180):
        srl.write(chr(255))
        srl.write(chr(servo))
        srl.write(chr(angle))
    else:
        print("Angle =", angle + ",", "Servo =", servo)
        print("Servo angle must be an integer between 0 and 180")

def changeAngle(servo, angle, prev_angle):
    if(angle < 0 or angle > 180):
        print("Angle =", angle + ",", "Servo =", servo)
        print("Servo angle must be an integer between 0 and 180")
        return
    for ang in range(prev_angle, angle+1):
        move(servo, ang)
        time.sleep(time_delay)
    

if __name__ == 'main':
    # load image
    img = cv2.imread('45.png')
    # Mask Color
    color = 'any'
    
    # Constants to be defined
    shoulder = 0
    humerous = 0
    radi_ulna = 0
    claw = 0
    
    # Define Servos
    face_servo = 1
    shouder_servo = 2
    elbow_servo = 3
    claw_servo = 4
    finger_servo = 5
    
    # Define Current Servo Angles
    face_angle_cur = 0
    shoulder_angle_cur = 0
    elbow_angle_cur = 0
    claw_angle_cur = 0
    finger_angle_cur = 0
    
    # Robotic Hand cooridinate
    cx_robot = 0
    cy_robot = int(np.size(img,0) / 2)
    # get all the contours from Object Detection
    cnts = od.giveContours(img, color)
    
    for cnt in cnts:
        (cx_cnt_f,cy_cnt_f) = od.contourCenter(cnt)
        cx_cnt = int(cx_cnt_f)
        cy_cnt = int(cy_cnt_f)
        
        # distance between base and object
        distance = np.sqrt((cx_cnt - cx_robot)**2 + (cy_cnt-cy_robot)**2)
        # distance between shoulder and wrist
        distance_ = np.sqrt((claw - shoulder) ** 2 + distance ** 2)
        
        # Servo 1 Angle
        try:
            face_angle = np.arctan((cy_cnt - cy_robot)/(cx_cnt - cx_robot))
        except:
            face_angle = np.pi/2
        
        # Servo Angles in order 2 to 5
        shoulder_angle = np.pi/2 + np.arccos((humerous**2 + distance_**2 - radi_ulna**2) / (2*humerous*distance_)) + np.arctan((claw - shoulder) / distance)
        elbow_angle = np.arccos((humerous**2 + radi_ulna**2 - distance_**2) / (2*humerous*radi_ulna))
        finger_angle = 0
    