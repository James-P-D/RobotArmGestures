import cv2              # pip install opencv-python
import mediapipe as mp  # pip install mediapipe
from math import hypot
#from ArmController import *
import xarm      # pip install xarm, pip install hidapi
from StopWatch import *
from statistics import median

PALM              = 0
THUMB             = 4
INDEX             = 8
MIDDLE            = 12
RING              = 16
PINKY             = 20

BLUE              = (255, 0, 0)
GREEN             = (0, 255, 0)
RED               = (0, 0, 255)
CYAN              = (255, 255, 0)
PURPLE            = (255, 0, 255)
YELLOW            = (0, 255, 255)
BLACK             = (0, 0, 0)

DOT_SIZE          = 5
LINE_SIZE         = 1

CALIBRATION       = 5
BUFFER_PERCENTAGE = 20

class PHASES:
    STRETCH       = 1
    CLENCH        = 2
    RELAX         = 3
    RUNNING       = 4

################################################
# Servo Constants
################################################

MIN_POS                   = 100
MAX_POS                   = 900

STEP                      = 50
DURATION                  = 100

class SERVOS:
    PINCER                = 1
    PINCER_TURN           = 2
    WRIST                 = 3
    ELBOW                 = 4
    SHOULDER              = 5
    BASE                  = 6

#############################################
# Globals
#############################################

arm = xarm.Controller('USB') # arm is the first xArm detected which is connected to USB

#############################################
# update_palm()
#############################################

def update_palm(digit, lm_list, img, color):
    (palm_x, palm_y) = lm_list[digit][1], lm_list[digit][2]
    cv2.circle(img, (palm_x, palm_y), DOT_SIZE, color, cv2.FILLED)
    return(palm_x, palm_y)

#############################################
# update_digit()
#############################################

def update_digit(digit, lm_list, palm_pos, img, color):
    (palm_x, palm_y) = palm_pos
    (digit_x, digit_y) = lm_list[digit][1], lm_list[digit][2]
    cv2.circle(img, (digit_x, digit_y), DOT_SIZE, color, cv2.FILLED)
    cv2.line(img, (digit_x, digit_y), (palm_x, palm_y), color, LINE_SIZE)                
    return(digit_x, digit_y, hypot(palm_x - digit_x, palm_y - digit_y))

#############################################
# reset_arm()
#############################################

def reset_arm():
    for servo_no in range(1, 7):
        servo = arm.setPosition(servo_no, 500, wait=False)

#############################################
# get_new_servo_position()
#############################################

def get_new_servo_position(servo_no, positive_direction):
    current_pos = arm.getPosition(servo_no)
    new_pos = min([current_pos+STEP, MAX_POS]) if positive_direction else max([current_pos-STEP, MIN_POS])

    match(servo_no):
        case SERVOS.BASE:
            return [SERVOS.BASE, new_pos]
        case SERVOS.SHOULDER:
            return [SERVOS.SHOULDER, new_pos]
        case SERVOS.ELBOW:
            return [SERVOS.ELBOW, new_pos]
        case SERVOS.WRIST:
            return [SERVOS.WRIST, new_pos]
        case SERVOS.PINCER_TURN:
            return [SERVOS.PINCER_TURN, new_pos]
        case SERVOS.PINCER:
            return [SERVOS.PINCER, new_pos]
    return []

#############################################
# Main()
#############################################

def main():
    reset_arm()

    video_capture = cv2.VideoCapture(0) 
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands()
    mp_draw = mp.solutions.drawing_utils


    phase = PHASES.STRETCH
    (thumb_list, thumb_max_dist, thumb_min_dist, thumb_mid_dist, thumb_buffer) = ([], None, None, None, None)
    (index_list, index_max_dist, index_min_dist, index_mid_dist, index_buffer) = ([], None, None, None, None)
    (middle_list, middle_max_dist, middle_min_dist, middle_mid_dist, middle_buffer) = ([], None, None, None, None)
    (ring_list, ring_max_dist, ring_min_dist, ring_mid_dist, ring_buffer) = ([], None, None, None, None)
    (pinky_list, pinky_max_dist, pinky_min_dist, pinky_mid_dist, pinky_buffer) = ([], None, None, None, None)

    (old_palm_x, old_palm_y) = (None, None)
    (min_thumb_dist, max_thumb_dist) = (None, None)
    stop_watch = StopWatch()
    stop_watch.start(CALIBRATION)
    while True:
        if (cv2.waitKey(1) & 0xff == 27): # Press ESC to exit
            break

        (success, img) = video_capture.read()
        if(not success):
            print("Unable to get video feed!")
            break        

        img_RGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        hand_results = hands.process(img_RGB)
        lm_list = []
        if hand_results.multi_hand_landmarks: 
            if(len(hand_results.multi_hand_landmarks) != 1):
                cv2.imshow("Image", img) 
                print("Waiting for single hand..")
                stop_watch.start(CALIBRATION)
                continue
            
            hand_landmark = hand_results.multi_hand_landmarks[0]
            for id, lm in enumerate(hand_landmark.landmark):
                (height, width, _) = img.shape
                (x, y) = int(lm.x * width), int(lm.y * height)
                lm_list.append([id, x, y]) 
            mp_draw.draw_landmarks(img, hand_landmark, mp_hands.HAND_CONNECTIONS)
            if lm_list != []:
                (palm_x, palm_y) = update_palm(PALM, lm_list, img, YELLOW)
                
                (thumb_x, thumb_y, thumb_dist) = update_digit(THUMB, lm_list, (palm_x, palm_y), img, BLUE)                
                (index_x, index_y, index_dist) = update_digit(INDEX, lm_list, (palm_x, palm_y), img, GREEN)
                (middle_x, middle_y, middle_dist) = update_digit(MIDDLE, lm_list, (palm_x, palm_y), img, RED)                
                (ring_x, ring_y, ring_dist) = update_digit(RING, lm_list, (palm_x, palm_y), img, CYAN)                
                (pinky_x, pinky_y, pinky_dist) = update_digit(PINKY, lm_list, (palm_x, palm_y), img, PURPLE)
                
                match phase:
                    case PHASES.STRETCH:
                        thumb_list.append(thumb_dist)
                        index_list.append(index_dist)
                        middle_list.append(middle_dist)
                        ring_list.append(ring_dist)
                        pinky_list.append(pinky_dist)
                        if(stop_watch.has_elapsed()):
                            (thumb_max_dist, index_max_dist, middle_max_dist, ring_max_dist, pinky_max_dist ) = (max(thumb_list), max(index_list), max(middle_list), max(ring_list), max(pinky_list))
                            (thumb_list, index_list, middle_list, ring_list, pinky_list) = ([], [], [], [], [])
                            phase = PHASES.CLENCH
                            stop_watch.start(CALIBRATION)                        
                        else:
                            print("Stretch hand for {:.2f} more seconds..".format(stop_watch.time_left()))                        
                    case PHASES.CLENCH:
                        thumb_list.append(thumb_dist)
                        index_list.append(index_dist)
                        middle_list.append(middle_dist)
                        ring_list.append(ring_dist)
                        pinky_list.append(pinky_dist)
                        if(stop_watch.has_elapsed()):
                            (thumb_min_dist, index_min_dist, middle_min_dist, ring_min_dist, pinky_min_dist ) = (min(thumb_list), min(index_list), min(middle_list), min(ring_list), min(pinky_list))
                            (thumb_list, index_list, middle_list, ring_list, pinky_list) = ([], [], [], [], [])
                            phase = PHASES.RELAX
                            stop_watch.start(CALIBRATION)                        
                        else:
                            print("Clench hand for {:.2f} more seconds..".format(stop_watch.time_left()))   
                    case PHASES.RELAX:
                        thumb_list.append(thumb_dist)
                        index_list.append(index_dist)
                        middle_list.append(middle_dist)
                        ring_list.append(ring_dist)
                        pinky_list.append(pinky_dist)
                        if(stop_watch.has_elapsed()):
                            (thumb_mid_dist, index_mid_dist, middle_mid_dist, ring_mid_dist, pinky_mid_dist ) = (median(thumb_list), median(index_list), median(middle_list), median(ring_list), median(pinky_list))
                            (thumb_list, index_list, middle_list, ring_list, pinky_list) = ([], [], [], [], [])
                            
                            print(f"Thumb min={thumb_min_dist}, mid={thumb_mid_dist}, max={thumb_max_dist}")
                            print(f"Index min={index_min_dist}, mid={index_mid_dist}, max{index_max_dist}")
                            print(f"Middle min={middle_min_dist}, mid={middle_mid_dist}, max{middle_max_dist}")
                            print(f"Ring min={ring_min_dist}, mid={ring_mid_dist}, max={ring_max_dist}")
                            print(f"Pinky min={pinky_min_dist}, mid={pinky_mid_dist}, max={pinky_max_dist}")
                            
                            if(not(thumb_min_dist < thumb_mid_dist < thumb_max_dist)):
                                print("Invalid thumb measurements. Recalibrating...")
                                phase = PHASES.STRETCH
                                stop_watch.start(CALIBRATION)                        
                                continue
                            elif(not(index_min_dist < index_mid_dist < index_max_dist)):
                                print("Invalid index measurements. Recalibrating...")
                                phase = PHASES.STRETCH
                                stop_watch.start(CALIBRATION)                        
                                continue
                            elif(not(middle_min_dist < middle_mid_dist < middle_max_dist)):
                                print("Invalid middle measurements. Recalibrating...")
                                phase = PHASES.STRETCH
                                stop_watch.start(CALIBRATION)                        
                                continue
                            elif(not(ring_min_dist < ring_mid_dist < ring_max_dist)):
                                print("Invalid ring measurements. Recalibrating...")
                                phase = PHASES.STRETCH
                                stop_watch.start(CALIBRATION)                        
                                continue
                            elif(not(pinky_min_dist < pinky_mid_dist < pinky_max_dist)):
                                print("Invalid pinky measurements. Recalibrating...")
                                phase = PHASES.STRETCH
                                stop_watch.start(CALIBRATION)                        
                                continue
                            else:
                                thumb_buffer = ((thumb_max_dist-thumb_min_dist) / 100 ) * BUFFER_PERCENTAGE
                                index_buffer = ((index_max_dist-index_min_dist) / 100 ) *  BUFFER_PERCENTAGE
                                middle_buffer = ((middle_max_dist-middle_min_dist) / 100 ) *  BUFFER_PERCENTAGE
                                ring_buffer = ((ring_max_dist-ring_min_dist) / 100 ) *  BUFFER_PERCENTAGE
                                pinky_buffer = ((pinky_max_dist-pinky_min_dist) / 100 ) *  BUFFER_PERCENTAGE
                                phase = PHASES.RUNNING
                        else:
                            print("Relax hand for {:.2f} more seconds..".format(stop_watch.time_left()))   

                    case PHASES.RUNNING:                 
                        servo_data = []
                        if ((old_palm_x != None) and (old_palm_y != None)):
                            palm_x_change = abs(palm_x-old_palm_x)
                            if (palm_x_change>10):
                                if (palm_x > old_palm_x):
                                    servo_data.append(get_new_servo_position(SERVOS.BASE, True))
                                elif (palm_x < old_palm_x):
                                    servo_data.append(get_new_servo_position(SERVOS.BASE, False))
                                (old_palm_x, old_palm_y) = (palm_x, palm_y)
                        else:
                            (old_palm_x, old_palm_y) = (palm_x, palm_y)

                        if (thumb_dist > (thumb_max_dist - thumb_buffer)):
                            servo_data.append(get_new_servo_position(SERVOS.PINCER, True))
                        elif (thumb_dist < (thumb_min_dist + thumb_buffer)):
                            servo_data.append(get_new_servo_position(SERVOS.PINCER, False)) 

                        if (index_dist > (index_max_dist - index_buffer)):
	                        servo_data.append(get_new_servo_position(SERVOS.SHOULDER, True))
                        elif (index_dist < (index_min_dist + index_buffer)):
	                        servo_data.append(get_new_servo_position(SERVOS.SHOULDER, False))

                        if (middle_dist > (middle_max_dist - middle_buffer)):
	                        servo_data.append(get_new_servo_position(SERVOS.ELBOW, True))
                        elif (middle_dist < (middle_min_dist + middle_buffer)):
	                        servo_data.append(get_new_servo_position(SERVOS.ELBOW, False))

                        if (ring_dist > (ring_max_dist - ring_buffer)):
	                        servo_data.append(get_new_servo_position(SERVOS.WRIST, True))
                        elif (ring_dist < (ring_min_dist + ring_buffer)):
	                        servo_data.append(get_new_servo_position(SERVOS.WRIST, False))

                        if (pinky_dist > (pinky_max_dist - pinky_buffer)):
	                        servo_data.append(get_new_servo_position(SERVOS.PINCER_TURN, True))
                        elif (pinky_dist < (pinky_min_dist + pinky_buffer)):
	                        servo_data.append(get_new_servo_position(SERVOS.PINCER_TURN, False))

                        # This should work, but is *incredibly* slow! Perhaps there's a bug in the lib..
                        #if (len(servo_data) > 0):
                        #    print(servo_data)
                        #    arm.setPosition(servo_data, DURATION, wait=True)

                        for item in servo_data:
                            arm.setPosition(item[0], item[1], DURATION, wait=True)
                        
                cv2.imshow("Image", img) 
        else:
            cv2.imshow("Image", img) 
            print("Waiting for single hand..")
            stop_watch.start(CALIBRATION)
            continue

#############################################
# Entry point
#############################################

if __name__ == "__main__":
    main()