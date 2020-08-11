import serial
import time
import keyboard

#time delay between consecutive angle changes
time_delay = 0.1

# Serial and Aduino Interaction
usbport = 'COM9'
srl = serial.Serial(usbport, 9600, timeout = 1)

# Define Current Servo Angles
face_angle_cur = 90
elbow_angle_cur = 0
claw_angle_cur = 0
finger_angle_cur = 0

# Define Servos
face_servo = 9

elbow_servo = 5
claw_servo = 4
finger_servo = 10
servoS1 = 3
servoS2 = 4
def move(servo, angle):
    print("yesssss")
    if(0 <= angle <= 180):
        srl.write(bytes(chr(255), 'UTF-8'))
        srl.write(bytes(chr(servo), 'UTF-8'))
        srl.write(bytes(chr(angle), 'UTF-8'))
        print("jkjkj")
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


def changeAngleS(angle, prev_angle):
    if(angle < 0 or angle > 180):
        print("Angle =", angle + ",", "Servo =", servoS1, servoS2)
        print("Servo angle must be an integer between 0 and 180")
        return
    for ang in range(prev_angle, angle+1):
        move(servoS1, ang)
        move(servoS2, 180-ang)
        time.sleep(time_delay)
        
def changeAngleFace(servo, angle, prev_angle):
    speed = 90
    if prev_angle > angle:
        speed += 5
    else:
        speed -= 5
    for ang in range(prev_angle, angle+1):
        srl.write(bytes(chr(255), 'UTF-8'))
        srl.write(bytes(chr(servo), 'UTF-8'))
        srl.write(bytes(chr(ang), 'UTF-8'))
        srl.write(bytes(chr(speed), 'UTF-8'))

def init():
    move(face_servo, face_angle_cur)
    move(elbow_servo, elbow_angle_cur)
    move(servoS1, 0)
    move(servoS2, 180)
    move(finger_servo, finger_angle_cur)
print("yesssss")
init()
#time.sleep(20)
print("yes")
while(True):
    # Face Angle
    if(keyboard.is_pressed('a')):
        print('a')
        changeAngleFace(face_servo, face_angle_cur - 1, face_angle_cur);
        face_angle_cur -= 1
    elif(keyboard.is_pressed('d')):
        print('d')
        changeAngle(face_servo, face_angle_cur + 1, face_angle_cur);
        face_angle_cur += 1
    # Shoulder Angle
    elif(keyboard.is_pressed('r')):
        print('r')
        changeAngleS(shoulder_angle_cur - 1, shoulder_angle_cur);
        shoulder_angle_cur -= 1
    elif(keyboard.is_pressed('t')):
        print('t')
        changeAngleS(shoulder_angle_cur + 1, shoulder_angle_cur);
        shoulder_angle_cur += 1
    # Elbow Angle
    elif(keyboard.is_pressed('e')):
        print('e')
        changeAngle(elbow_servo, elbow_angle_cur - 1, elbow_angle_cur);
        elbow_angle_cur -= 1
    elif(keyboard.is_pressed('f')):
        print('f')
        changeAngle(elbow_servo, elbow_angle_cur + 1, elbow_angle_cur);
        elbow_angle_cur += 1
    # Claw Angle
    elif(keyboard.is_pressed('b')):
        print('b')
        changeAngle(claw_servo, claw_angle_cur - 1, claw_angle_cur);
        claw_angle_cur -= 1
    elif(keyboard.is_pressed('c')):
        print('c')
        changeAngle(claw_servo, claw_angle_cur + 1, claw_angle_cur);
        claw_angle_cur += 1
    # Finger Angle
    elif(keyboard.is_pressed('g')):
        print('g')
        changeAngle(finger_servo, finger_angle_cur - 1, finger_angle_cur);
        finger_angle_cur -= 1
    elif(keyboard.is_pressed('h')):
        print('h')
        changeAngle(finger_servo, finger_angle_cur + 1, finger_angle_cur);
        finger_angle_cur += 1
    elif(keyboard.is_pressed('q')):
        break
    time.sleep(0.1)
