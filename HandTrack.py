import cv2
import mediapipe as mp
import time

cap=cv2.VideoCapture(0) #video capture object representing camera

if not cap.isOpened():
    print("Error: Could not open webcam. Try changing the index (0, 1, 2...)")
    exit()

mpHands=mp.solutions.hands # mediapipe->solutions->hands module is imported and assigned to mpHands
hands=mpHands.Hands() 
# (static_image_mode=False(def) : if cant track i.e confidence goes below a certain pt then detect...if true then detect only hence slow)
# max_num_hands=2(def)
# min_detection_confidence=0.5(def)
# min_tracking_confidence=0.5(def)
mpDraw=mp.solutions.drawing_utils # mediapipe->solutions->drawing_utils module is imported and assigned to mpDraw for drawing the landmarks and connections on the img

pTime=0 #previous time
cTime=0 #current time

while(True):
  success,img=cap.read() #returns a boolean if a frame was successfully captured or not and the numpy array of px of img data stream

  imgRGB=cv2.cvtColor(img,cv2.COLOR_BGR2RGB) #converts the color space of the img from BGR to RGB
  results=hands.process(imgRGB) #processes the img and returns the results of the hand detection and tracking

  #extracting multi_hand_landmarks from results
  if results.multi_hand_landmarks: #if any hand is detected
    for handLms in results.multi_hand_landmarks: #for each hand detected
      for id,lm in enumerate(handLms.landmark): #enumerate returns the index and the value of the landmark
        h,w,c=img.shape #height, width, channels of the img
        cx,cy=int(lm.x*w),int(lm.y*h) #converting the normalized landmark coordinates to pixel coordinates
        #each landmark has an id and a normalized coordinate (x,y,z) in the range [0,1] where (0,0) is the top-left corner and (1,1) is the bottom-right corner of the img and we'll use the x,y coords to find the location of the landmark in the img
        print(id,cx,cy) #printing the id and the pixel coordinates of the landmark

        if id==12: #if the landmark is the tip of the thumb
          cv2.circle(img,(cx,cy),15,(255,0,255),cv2.FILLED) #draws a filled circle on the img at the pixel coordinates of the landmark with radius 15 and color blue (BGR)
          #can select any landmark id from 0 to 20 and perform any operation on it like drawing a circle, line, etc. or use the coordinates for any other purpose


      mpDraw.draw_landmarks(img,handLms,mpHands.HAND_CONNECTIONS) 
      #draws the landmarks and connections on the original BGR img...handLms is the landmark data and mpHands.HAND_CONNECTIONS is the connection data for the hand


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