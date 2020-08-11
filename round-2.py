import cv2
import numpy as np
import math, time
import serial
import TestCentre
usbport = 'COM4'
color_done = 0
# Set up serial baud rate
ser = serial.Serial(usbport, 9600, timeout=1)
flag = 0
center_x = 0
center_y = 0
time_delay = 0.02    #time_delay b/w angle angle changes        
def move(servo, angle):
    '''Moves the specified servo to the supplied angle.
    Arguments:
        servo
          the servo number to command, an integer from 1-4
        angle
          the desired servo angle, an integer from 0 to 180

    (e.g.) >>> servo.move(2, 90)
           ... # "move servo #2 to 90 degrees"'''

    if (0 <= angle <= 180):
        ser.write(chr(255))
        ser.write(chr(servo))
        ser.write(chr(angle))
    else:
        print("Angle is ", angle)
        print("Servo angle must be an integer between 0 and 180.\n")
#To move angle slowly
def changeAngle(servo, angle, from_angle):

    if(angle > from_angle):
        for a in range(from_angle, angle, 1):
            move(servo, a)
            time.sleep(time_delay)
    else:
        for a in range(from_angle, angle, -1):
            move(servo, a)
            time.sleep(time_delay)
            
# Set bot to initial position
def init():
    changeAngle(1,0,90)           #Anticlockwise Rotation
    changeAngle(2,180,90)         #Clockwise Rotation
    changeAngle(3,0,90)           #Radius-Ulna
    changeAngle(4,70,90)          #Humerus
    move(5,0)
    move(6,0)

init()

#input()

t = 5;              #time for which arm should be stopped at a red square
angle = 0           #main rotation angle
pre_angle = 0       #previous main rotation angle
theta1 = 0          #shoulder
theta2 = 0          #elbow

#black
lowerBound0=np.array([0,0,0])
upperBound0=np.array([255,255,70])
#red1
lowerBound3a=np.array([0,100,84])
upperBound3a=np.array([20,255,255])
#red2
lowerBound3b=np.array([170,100,100])
upperBound3b=np.array([179,255,255])
#green
lowerBound1=np.array([50,80,40])
upperBound1=np.array([80,255,255])
#blue
lowerBound2=np.array([100,86,40])
upperBound2=np.array([130,255,255])
#yellow
lowerBound4=np.array([20,100,100])
upperBound4=np.array([40,255,255])

l1 = 150            #Humerus
l2 = 150            #Radius-Ulna
h = 75              #Height = 12.5 cm

kernelOpen=np.ones((5,5))
kernelClose=np.ones((5,5))

def pop(theta1,theta2):
    if flag is 0:
        changeAngle(3, theta2/2,0)
    else:
        changeAngle(3, theta2/2,130)
    move(3,theta2 + 10)
    changeAngle(3,130, theta2 + 10)
    changeAngle(4,80,theta1)
    flag = 1

# To Draw Contour, get it's centre and other stuff
def ContourDetection(color, imgHSV, pre_angle):
    #pre_angle = 0
    
    # Contour Detection by Color 0=Black, 1=Green, 2=Blue, 3=Red, 4=yellow
    if color is 0:
        mask1G=cv2.inRange(imgHSV,lowerBound0,upperBound0)
    elif color is 1:
        mask1G=cv2.inRange(imgHSV,lowerBound1,upperBound1)
    elif color is 2:
        mask1G=cv2.inRange(imgHSV,lowerBound2,upperBound2)
    elif color is 3:
        mask1Ga=cv2.inRange(imgHSV,lowerBound3a,upperBound3a)
        mask1Gb=cv2.inRange(imgHSV,lowerBound3b,upperBound3b)
        mask1G = mask1Ga + mask1Gb
    elif color is 4:
        mask1G=cv2.inRange(imgHSV,lowerBound4,upperBound4)
        
    mask2G=cv2.morphologyEx(mask1G,cv2.MORPH_OPEN,kernelOpen)
    mask3G=cv2.morphologyEx(mask2G,cv2.MORPH_CLOSE,kernelClose)
    _, contoursG, _ =cv2.findContours(mask3G,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
    
    #Algorithm on Contour
    for contour in contoursG:
        area=cv2.contourArea(contour)
       
        if(8000> area > 2000):                #To reduce noise
            cv2.drawContours(img,contour,-1,(160,32,240),2)
            # Moments used for finding center
            M = cv2.moments(contour)
            try:
                Cx = float(M['m10']/M['m00'])
                Cy = float(M['m01']/M['m00'])
            except:
                Cx = center_x
                Cy = center_y
            cv2.circle(img,(int(Cx),int(Cy)),5, (160,32,240), -1 )
            #print(Cx,Cy)
            dist=int(math.sqrt((center_x-Cx)*(center_x-Cx)+(center_y-Cy)*(center_y-Cy)))            #Distance
            #angle
            if(Cx!=center_x):
                angle=int(180*(np.arctan((center_y-Cy)/(-center_x+Cx)))/np.pi)
            
            else:
                if Cy > center_y:
                    angle = -90
                else:
                    angle = 90
        
            if Cx < center_x and Cy < center_y:
                angle = angle + 180
            elif Cx < center_x and Cy > center_y:
                angle = angle - 180
                
            print("A",angle)
            print("D",dist)

            try:
                theta2 = int(180*np.arccos(float((l1*l1 + l2*l2 - h*h - dist*dist))/(2*l1*l2))/np.pi)          #theta2
                print("COS(theta2) = " , (l1*l1 + l2*l2 - h*h - dist*dist)/(2*l1*l2))
            except:
                print(180*np.arccos((l1*l1 + l2*l2 - h*h - dist*dist)/(2*l1*l2))/np.pi)
            k1 = dist*dist + l1*l1 - l2*l2 + h*h
            k2 = 2*dist*l1
            k3 = 2*h*l1
            
            theta1 = int(180/np.pi*(np.arccos(h/np.sqrt(h*h+dist*dist))+np.arccos(k1/(2*l1*np.sqrt(dist*dist+h*h)))))     #theta1
            
            print("$",theta1,theta2)
        
            # Changle Angle of Pop-Eye Hand
            if pre_angle >= 0:
                if angle >= 0:
                    changeAngle(1,int(angle), int(pre_angle))
                else:
                    changeAngle(1,0,int(pre_angle))
                    changeAngle(2,180 + int(angle), 180)
            else:
                if angle>= 0:
                    changeAngle(2,180, int(pre_angle))
                    changeAngle(1,int(angle),0)
                else:
                    changeAngle(2,180 + int(angle), 180 + int(pre_angle))
                   
            #Change Angle of Shoulder - 4 and Elbow - 3   
            try:
                if(flag is 1):
                    changeAngle(4, 70+int(180-theta1), 70)
                    pop(int(70+int(180-theta1)), int(180-theta2))
            except:
                print("0")
            pre_angle = int(angle)
            time.sleep(t)

            #change angle by 180
            if angle > 0:
                angle = angle - 180
            else:
                angle = angle + 180
            
            
#Main Program
cam = cv2.VideoCapture(0)
while True:
    img = cv2.imread('1.jpg')
    #_, img = cam.read()
    #img = cv2.resize(img,(500,500))
    min_x,min_y,max_x,max_y = TestCentre.centers_required(img)
    scale = (max_x + max_y - min_x - min_y)/180
    if scale != 0:
        h = int(12.5*(max_x + max_y - min_x - min_y)/180)
        l1 = int(26.5*(max_x + max_y - min_x - min_y)/180)
        l2 = int(32*(max_x + max_y - min_x - min_y)/180)
    else:
        h = 100
        l1 = 212
        l2 = 256
    print("S, H, L1, L2", scale, h, l1, l2)

    center_x = min_x /2 + max_x / 2
    center_y = min_y/2 + max_y /2
    cv2.circle(img,(center_x,center_y),5,(160,32,240), -1)
    #img=cv2.resize(img,(500,500))
    bluredimg=cv2.GaussianBlur(img,(5,5),0)
    imgHSV=cv2.cvtColor(bluredimg,cv2.COLOR_BGR2HSV)
    #Detect Red Contours

    if color_done is 3:
        ContourDetection(3, imgHSV, pre_angle) #0=Black, 1=Green, 2=Blue, 3=Red, 4=Yellow
    if color_done is 2:
        ContourDetection(2, imgHSV, pre_angle) #0=Black, 1=Green, 2=Blue, 3=Red, 4=Yellow
    if color_done is 1:
        ContourDetection(1, imgHSV, pre_angle) #0=Black, 1=Green, 2=Blue, 3=Red, 4=Yellow
    if color_done is 4:
        ContourDetection(4, imgHSV, pre_angle) #0=Black, 1=Green, 2=Blue, 3=Red, 4=Yellow
    cv2.imshow("Round1",img)
    if cv2.waitKey(1) & 0xFF==ord('q'):
        break
#cv2.waitKey(0)
cam.release()
cv2.destroyAllWindows()


