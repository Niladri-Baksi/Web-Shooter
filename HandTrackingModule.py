import cv2
import mediapipe as mp
import time


class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5): #__init__ is a constructor. It runs automatically when you create an object of the class. self is the object itself. It is used to access the attributes and methods of the class. mode, maxHands, detectionCon, trackCon are the parameters of the constructor. They are used to initialize the attributes of the class. The default values are set to False, 2, 0.5, 0.5 respectively.
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        #initializations
        self.mpHands = mp.solutions.hands  # mediapipe->solutions->hands module is imported and assigned to mpHands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        # (static_image_mode=False(def) : if cant track i.e confidence goes below a certain pt then detect...if true then detect only hence slow)
        # max_num_hands=2(def)
        # min_detection_confidence=0.5(def)
        # min_tracking_confidence=0.5(def)
        self.mpDraw = mp.solutions.drawing_utils  # mediapipe->solutions->drawing_utils module is imported and assigned to mpDraw for drawing the landmarks and connections on the img

##detection##
    def findHands(self, img, draw=True): #findHands is a method of the class handDetector. It takes an image as input and returns the image with the hand landmarks drawn on it. draw is a boolean parameter that determines whether to draw the landmarks or not. The default value is True.

        imgRGB=cv2.cvtColor(img,cv2.COLOR_BGR2RGB) #converts the color space of the img from BGR to RGB
        self.results=self.hands.process(imgRGB) #processes the img and returns the results of the hand detection and tracking

        #extracting multi_hand_landmarks from results
        if self.results.multi_hand_landmarks: #if any hand is detected
            for handLms in self.results.multi_hand_landmarks: #for each hand detected


                # drawing the landmarks and connections on the img

                landmark_spec = self.mpDraw.DrawingSpec(
                color=(0, 255, 0),
                thickness=2,
                circle_radius=1
                )

                connection_spec = self.mpDraw.DrawingSpec(
                    color=(200, 0, 200),
                    thickness=2
                )


                if draw:
                    self.mpDraw.draw_landmarks(img,handLms,self.mpHands.HAND_CONNECTIONS, landmark_spec, connection_spec)
                    #draws the landmarks and connections on the original BGR img...handLms is the landmark data and self.mpHands.HAND_CONNECTIONS is the connection data for the hand
        return img



    def findPosition(self, img, handNo=0, draw=False): #findPosition is a method of the class handDetector. It takes an image as input and returns a list of the pixel coordinates of the landmarks of the specified hand. handNo is an integer parameter that determines which hand to track. The default value is 0 (the first hand detected). draw is a boolean parameter that determines whether to draw the landmarks or not. The default value is True.
        lmList = [] #list to store the pixel coordinates of the landmarks
        if self.results.multi_hand_landmarks: #if any hand is detected
            if handNo < len(self.results.multi_hand_landmarks): 
                myHand = self.results.multi_hand_landmarks[handNo] #get the specified hand
                for id, lm in enumerate(myHand.landmark): #enumerate returns the index and the value of the landmark
                    h, w, c = img.shape #height, width, channels of the img
                    cx, cy = int(lm.x * w), int(lm.y * h) #converting the normalized landmark coordinates to pixel coordinates
                    lmList.append([id, cx, cy]) #append the id and the pixel coordinates of the landmark to the list
                    if draw:
                        cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED) #draws a filled circle on the img at the pixel coordinates of the landmark with radius 5 and color green (BGR)
        return lmList


def main():
    pTime=0 #previous time
    cTime=0 #current time
    cap=cv2.VideoCapture(1) #video capture object representing camera
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    if not cap.isOpened():
        print("Error: Could not open webcam. Try changing the index (0, 1, 2...)")
        exit()
    detector = handDetector() #creating an object of the class handDetector
    while(True):
        success,img=cap.read() #returns a boolean if a frame was successfully captured or not and the numpy array of px of img data stream
        if not success:
            print("Failed to capture frame")
            break
        img=detector.findHands(img) #calling the findHands method of the class handDetector to detect and draw the hand landmarks on the img

        lmList = detector.findPosition(img) #calling the findPosition method of the class handDetector to get the pixel coordinates of the landmarks of the first hand detected
        if len(lmList) != 0: #if any hand is detected
            print(lmList[4]) #printing the pixel coordinates of the tip of the thumb (landmark id 4)


        cTime=time.time() #current time in seconds
        fps=1/(cTime-pTime) #calculating the fps by taking the reciprocal
        pTime=cTime #updating the previous time
        cv2.putText(img, f'FPS: {int(fps)}', (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3) #putting the fps on the img at (10,70) with font size 3 and color blue (BGR) and thickness 3
    
        cv2.imshow("Image",img) # a img window is created and the img is shown
    
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        # keep the window responsive by waiting for 1ms to update/response and to chk if a key was pressed
        # waitkey value (bitwise &) with 0xFF(hexadecimal for 255 or 11111111) hence returning that response itself It's commonly used to make the returned keyboard value compatible across different systems/OpenCV setups.
        # ord('q') converts the character 'q' into its numeric character code. 113
    
        # cv2.waitKey(1) 



if __name__=="__main__":
    main()