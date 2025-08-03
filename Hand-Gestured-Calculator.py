import cv2
import mediapipe as mp
import math
import time
from collections import deque
import numpy as np

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
is_symbol = False
expression = []
last_symbol= None
last_number = None
symbol_cooldown = time.time()
number_cooldown = time.time()
last_detected_time = 0
gesture_delay = 3.0
number_delay = 3.0
show_result = None
show_result_until = 0

# for finding zero
def is_zero(lm,label):
    if label == 'Right':
        thumb = lm[4].x < lm[3].x
    else:
        thumb = lm[4].x > lm[3].x
    index = lm[6].y > lm[8].y
    middle = lm[10].y > lm[12].y
    ring = lm[14].y > lm[16].y
    pinky = lm[18].y > lm[20].y
    return not(thumb or index or middle or ring or pinky)

#new function for all symbols
def get_angle(x1,y1,x2,y2):
    radians = math.atan2(y2-y1,x2-x1)
    degrees = math.degrees(radians)
    return  abs(degrees)

def is_done_gesture(lm):
    thumb_angle = get_angle(lm[0].x,lm[0].y,lm[4].x,lm[4].y)
    thumbs_up = 45 < thumb_angle < 135
    index_folded = lm[8].y > lm[6].y
    middle_folded = lm[12].y > lm[10].y
    ring_folded = lm[16].y > lm[14].y
    pinky_folded = lm[20].y > lm[18].y
    return thumbs_up and index_folded and middle_folded and ring_folded and pinky_folded

def detect_symbol(hands,handedness_list):
    if not hands:
        return None
    #single hand gestures
    if len(hands) == 1:
        lm = hands[0].landmark
        hand_label = handedness_list[0].classification[0].label
        angle = get_angle(lm[0].x, lm[0].y, lm[8].x, lm[8].y)
        if hand_label != 'Left':
            return None
        #detects sign - minus
        if 150 <= angle <=180:
            return '-'
        
        #detects sign - divide        
        if (30 <= angle <= 70) or (110 <= angle <= 150):
            return '/'
        
        #detects sign - Equals
        if is_done_gesture(lm) and hand_label == 'Left':
            return '='
    
    elif len(hands) == 2:
        lm1 = hands[0].landmark
        lm2 = hands[1].landmark
        
        #angle for both hands
        angle1 = get_angle(lm1[0].x, lm1[0].y, lm1[8].x, lm1[8].y)
        angle2 = get_angle(lm2[0].x, lm2[0].y, lm2[8].x, lm2[8].y)
        wrist_dist = math.hypot(lm1[0].x - lm2[0].x, lm1[0].y - lm2[0].y)
        
        #detects sign - plus
        is_hand1_horizontal = angle1 >= 150 or angle1 <= 30
        is_hand1_vertical = 60 <= angle1 <= 120
        is_hand2_horizontal = angle2 >= 150 or angle2 <= 30
        is_hand2_vertical = 60 <= angle2 <= 120

        plus_using_lefthand = is_hand1_horizontal and is_hand2_vertical
        plus_using_righthand = is_hand2_horizontal and is_hand1_vertical        
        if  (plus_using_lefthand or plus_using_righthand) and wrist_dist < 0.1:
            return '+'
        
        #detects sign - multiply
        cond1 = 30 <= angle1 <= 80 and 100 <= angle2 <= 150
        cond2 = 30 <= angle2 <= 80 and 100 <= angle1 <= 150
        if  (cond1 or cond2) and wrist_dist < 0.1:
            return '*'
        
        #detects sign - floor division
        left_side_signing = (30 <= angle1 <= 80 and 30 <= angle2 <= 80)
        right_side_signing = (100 <= angle1 <= 150 and 100 <= angle2 <= 150)
        if  left_side_signing or right_side_signing:
            return '//'
        return None
    return None


#new function for all symbols

#FOR OPENING WEBCAM AND READING FRAMES
webcam = cv2.VideoCapture(0)
#For Resizable Window
cv2.namedWindow('WebCam feed Live', cv2.WINDOW_NORMAL)
cv2.resizeWindow('WebCam feed Live',1000,800)

if not webcam.isOpened():
    print('error opening webcam: ')
    exit()
print('Starting in 5 seconds')
time.sleep(5)
print('Go!!')

with mp_hands.Hands(
    max_num_hands = 4,
    min_detection_confidence = 0.7,
    min_tracking_confidence = 0.5 ) as hands:
    hand_stable_count = 0
    last_finger_count = -1
    while True:
        ret, frame = webcam.read()
        if not ret:
            print(" error reading frame ")
            break
        
        frame = cv2.flip(frame,1)
        image  = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        result = hands.process(image)

        finger_count = 0
        left_count = 0
        right_count = 0
        left_zero = False
        right_zero = False
        
        if result.multi_hand_landmarks and result.multi_handedness:
            num_hands = len(result.multi_hand_landmarks)
            symbol = None
            if num_hands <=2:
                symbol = detect_symbol(result.multi_hand_landmarks, result.multi_handedness)
            if num_hands >=2:
                    is_symbol = True
            for hand_landmarks, hand_handedness in zip(result.multi_hand_landmarks, result.multi_handedness):
                mp_drawing.draw_landmarks(
                                      frame,
                                      hand_landmarks,
                                      mp_hands.HAND_CONNECTIONS,
                                      mp_drawing.DrawingSpec(color = (255,255,255), thickness = 2, circle_radius = 2),
                                      mp_drawing.DrawingSpec(color=(0,0,0), thickness = 2)
                                      )
                label = hand_handedness.classification[0].label
                lm = hand_landmarks.landmark                
                                
                if symbol and symbol != last_symbol:
                    current_time = time.time()
                    if current_time - last_detected_time < gesture_delay:
                        continue
                    last_detected_time = current_time
                    expression.append(symbol)
                    last_symbol = symbol
                    cv2.putText(frame,f'sign: {symbol}', (10,100),
                                cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,0),3)
                    if symbol == '=':
                        try:
                            joined = ' '.join(str(e) for e in expression[:-1])
                            total = eval(joined)                            
                            show_result = total
                            show_result_until = time.time()+10
                            expression.clear()
                            last_number = None
                            last_symbol = None
                            is_symbol = True
                        except:                        
                            expression.clear()
                else:
                    if symbol != last_symbol:
                        last_symbol = None
                number_cooldown = time.time() + 2.0        
                if  label == 'Right' and is_zero(lm,label): #detecting zero
                    right_zero = True
                    continue
                if not is_symbol and label == 'Right': #right hand
                    if lm[4].x < lm[3].x:  # right thumb
                        right_count += 5
                    if lm[8].y < lm[6].y: #index
                        right_count += 1
                    if lm[12].y < lm[10].y: #middle
                        right_count += 1
                    if lm[16].y < lm[14].y: #ring
                        right_count += 1
                    if lm[20].y < lm[18].y: #pinky
                        right_count += 1


        finger_count = right_count                
        current_time = time.time()
        if not is_symbol:
            if finger_count == last_finger_count and finger_count != 0:
                hand_stable_count +=1
            else:
                hand_stable_count = 0
            last_finger_count = finger_count
            if hand_stable_count >= 3 and finger_count != last_number:
                expression.append(finger_count)
                last_number = finger_count
                hand_stable_count = 0
                number_cooldown = current_time


        is_symbol = False                
        cv2.putText(frame,f'Number : {finger_count}',(10,50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 3)

        cv2.putText(frame,f' Expression: {" ".join(map(str,expression))}',(10,200),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 2)

        if show_result and time.time() < show_result_until:
            cv2.putText(frame,f' Result: {show_result}',(10,150),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 3)
        else:
            show_result = None
        cv2.imshow("WebCam feed Live", frame)
        key = cv2.waitKey(1)
        if  key == 27:
            break


webcam.release()
cv2.destroyAllWindows()


