import cv2
import numpy as np
import imutils

# Returns Shape of the supplied Contour
def contourShape(cnt):
    peri = cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, 0.04*peri, True)
    shape = ""
    
    if(len(approx) == 3):
        shape = "Triangle"
    elif(len(approx) == 4):
        shape = "Quadrilateral"
        x,y,w,h = cv2.boundingRect(cnt)
        ratio = float(w)/h;
        if ratio > 0.9 and ratio < 1.1:
            shape = "Square"
        else:
            shape = "Rectangle"
    elif(len(approx) == 5):
        shape = "Pentagon"
    elif(len(shape) == 6):
        shape = "Hexagon"
    else:
        shape = "Circle"
    return shape

# return mask of th given color from the supplied image
def maskColor(img, color):
    #black
    lowerBoundBlack = np.array([0,0,0])
    upperBoundBlack = np.array([255,255,70])
    #orange
    lowerBoundOrange = np.array([10,100,100])
    upperBoundOrange = np.array([20,255,255])
    #red1
    lowerBoundRedLow = np.array([0,100,100])
    upperBoundRedLow = np.array([10,255,255])
    #red2
    lowerBoundRedHigh = np.array([160,100,100])
    upperBoundRedHigh = np.array([179,255,255])
    #green
    lowerBoundGreen = np.array([50,80,40])
    upperBoundGreen = np.array([80,255,255])
    #blue
    lowerBoundBlue = np.array([100,86,40])
    upperBoundBlue = np.array([130,255,255])
    #yellow
    lowerBoundYellow = np.array([25,156,190])
    upperBoundYellow = np.array([62,181,250])
    #kernel to reduce noise
    kernel = np.ones((5,5))
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    if color == 'BLACK':
        mask = cv2.inRange(hsv, lowerBoundBlack, upperBoundBlack)
    elif color == 'ORANGE':
        mask = cv2.inRange(hsv, lowerBoundOrange, upperBoundOrange)
    elif color == 'RED':
        mask_low = cv2.inRange(hsv, lowerBoundRedLow, upperBoundRedLow)
        mask_high = cv2.inRange(hsv, lowerBoundRedHigh, upperBoundRedHigh)
        mask = cv2.bitwise_or(mask_low, mask_high)
    elif color == 'GREEN':
        mask = cv2.inRange(hsv, lowerBoundGreen, upperBoundGreen)
    elif color == 'BLUE':
        mask = cv2.inRange(hsv, lowerBoundBlue, upperBoundBlue)
    elif color == 'YELLOW':
        mask = cv2.inRange(hsv, lowerBoundYellow, upperBoundYellow)
    else:
        mask = cv2.inRange(hsv, np.array([0,0,0]), np.array([255,255,255]))
    
    mask_2 = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask_3 = cv2.morphologyEx(mask_2, cv2.MORPH_CLOSE, kernel)
    
    return mask_3
def giveContours(img, color):
    mask = maskColor(img, color.upper())
    mask_blur = cv2.GaussianBlur(mask, (5,5),2)
    img_mask = cv2.bitwise_and(img, img, mask = mask_blur)
    gray = cv2.cvtColor(img_mask,cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5,5),0)
    thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
    
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE);
    cnts = imutils.grab_contours(cnts)
    return cnts

def contourCenter(cnt):
    try:
        M = cv2.moments(cnt)
        cx = (M['m10']/M['m00'])
        cy = (M['m01']/M['m00'])
    except:
        cx = 0.0
        cy = 0.0
    return (cx, cy)
# Marks specified shapes of specified color from the given image
def showObjects(img, color, shape):
    resized = imutils.resize(img, width=300)
    ratio = img.shape[0] / float(resized.shape[0])
    cnts = giveContours(resized, color)
    
    flag = False
    shapes = {'TRIANGLE', 'RECTANGLE', 'SQUARE', 'PENTAGON', 'HEXAGON', 'CIRCLE'}
    for cnt in cnts:
        contour_shape = contourShape(cnt)
        if(contour_shape.upper() != shape.upper() and shape.upper() in shapes):
            continue;
        flag = True
        """
        try:
            M = cv2.moments(cnt)
            cx = int(M['m10']/M['m00'] * ratio)
            cy = int(M['m01']/M['m00'] * ratio)
        except:
            cx = 0
            cy = 0
        """
        (cx_f,cy_f) = contourCenter(cnt)
        cx = int(cx_f*ratio)
        cy = int(cy_f*ratio)
        cnt = cnt.astype("float")
        cnt *= ratio
        cv2.drawContours(img, [cnt.astype("int")], -1, (0,155,0), 2)
        cv2.putText(img, contour_shape, (cx,cy), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255,255,255), 2)
        cv2.imshow("contour",img)
        cv2.waitKey(0)
    else:
        if flag is False:
            print("NOT FOUND\nSHAPE =",shape.upper()+",", "COLOR =", color.upper())

# Main Program
if __name__ == '__main__':
    cap = cv2.VideoCapture(1)
    while(True):
        _, img = cap.read()
        showObjects(img, 'any', 'triangle')
    cap.release()
    cv2.destroyAllWindows()
