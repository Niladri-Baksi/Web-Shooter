########single splat###########

import cv2
import numpy as np
from HandTrackingModule import handDetector

cap = cv2.VideoCapture(0)
web_image = cv2.imread("white-spider-web-png-9.png", cv2.IMREAD_UNCHANGED) #imread_unchanged because we need the PNG's alpha/transparency channel
print(web_image.shape)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

detector = handDetector()

previous_thumb = False #remember the previous state of the thumb (extended or not)

web_active = False #Is there currently a web projectile flying?
web_distance = 0 #How far has the web travelled from where it started?
web_speed = 30
web_dx = 0
web_dy = 0

#where the web was fired from
web_start_x = 0
web_start_y = 0

web_splatter = False #whether the projectile has reached its final splatter stage

#where the splatter appears
web_splatter_x = 0
web_splatter_y = 0

#how long the splatter has existed
web_splatter_timer = 0

# #get the transparent web img and blend it on the cam feed
# def overlay_image(background, overlay, x, y):
#     h, w = overlay.shape[:2]
#     # Keep overlay inside the screen
#     if x < 0 or y < 0 or x + w > background.shape[1] or y + h > background.shape[0]:
#         return background
#     alpha = overlay[:, :, 3] / 255.0
#     for c in range(3):
#         background[y:y+h, x:x+w, c] = (
#             alpha * overlay[:, :, c] +
#             (1 - alpha) * background[y:y+h, x:x+w, c]
#         )
#     return background

def overlay_image(background, overlay, x, y):
    h, w = overlay.shape[:2]
    bg_h, bg_w = background.shape[:2]

    # figure out the overlapping region between the overlay and the screen
    x1, y1 = max(x, 0), max(y, 0)
    x2, y2 = min(x + w, bg_w), min(y + h, bg_h)

    if x1 >= x2 or y1 >= y2:
        return background  # completely off-screen, nothing to draw

    # corresponding crop of the overlay itself (in case x/y went negative)
    ox1, oy1 = x1 - x, y1 - y
    ox2, oy2 = ox1 + (x2 - x1), oy1 + (y2 - y1)

    overlay_crop = overlay[oy1:oy2, ox1:ox2]
    alpha = overlay_crop[:, :, 3] / 255.0

    for c in range(3):
        background[y1:y2, x1:x2, c] = (
            alpha * overlay_crop[:, :, c] +
            (1 - alpha) * background[y1:y2, x1:x2, c]
        )
    return background

while True:

    success, img = cap.read()

    if not success:
        print("Failed to capture frame")
        break

    img = detector.findHands(img)

    lmList = detector.findPosition(img)

    if len(lmList) != 0:


        # print("Index:", lmList[8])
        # print("Thumb:", lmList[4])
        # print("Pinky:", lmList[20])

        # x5, y5 = lmList[5][1], lmList[5][2]
        # x8, y8 = lmList[8][1], lmList[8][2]
        # index_distance = np.hypot(x8 - x5, y8 - y5)
        # print("Index distance:", int(index_distance))


        # x5, y5 = lmList[5][1], lmList[5][2]
        # x8, y8 = lmList[8][1], lmList[8][2]
        # index_distance = np.hypot(x8 - x5, y8 - y5)
        # #lm5 is the index finger base, lm8 is the index finger tip. The distance between them can be used to determine if the index finger is extended or not.

        # if index_distance > 150:
        #     index_extended = True
        # else:
        #     index_extended = False
        # print("Index extended:", index_extended)


        #index finger
        x5, y5 = lmList[5][1], lmList[5][2]
        x8, y8 = lmList[8][1], lmList[8][2]
        x17, y17 = lmList[17][1], lmList[17][2]


        index_length = np.hypot(x8 - x5, y8 - y5)
        hand_size = np.hypot(x17 - x5, y17 - y5)

        index_ratio = index_length / hand_size

        # print("Index ratio:", round(index_ratio, 2))
        # print("Index:", index_extended)

        index_extended = index_ratio > 0.8 #if index_ratio > 0.8:then the index finger is considered extended, otherwise it is considered not extended. since Index closed: ~0.4 Index extended: ~1.2 did moved far and close, approximately same values...so took a mid threshold value of 0.8 to determine if the index finger is extended or not.

        if index_extended:
            cv2.putText(
                img,
                "AIMING",
                (10, 200),
                cv2.FONT_HERSHEY_PLAIN,
                2,
                (0, 0, 255),
                2
            )

            #getting the diff between the index finger tip and base coordinates to calculate the direction of the index finger. x increases to the right, y increases downwards. 
            dx = x8 - x5 
            dy = y8 - y5 
            #drawing a line from the index finger tip to the direction it is pointing. The length of the line is 300 pixels. The end point of the line is calculated by adding the direction vector (dx, dy) to the index finger tip coordinates (x8, y8). 
            aim_length = 300
            end_x = int(x8 + dx / np.hypot(dx, dy) * aim_length)
            end_y = int(y8 + dy / np.hypot(dx, dy) * aim_length)
            #np.hypot(dx, dy) calculates the length or magnitude of the vector (dx, dy). then normalization or unit vector = vector/magnitude.
            #extend the direction from the tip i.e x8,y8 after multiplying by 300 px...so length of the line is 300 px. then add to the tip coordinates to get the end coordinates of the line.
            cv2.line(
                img,
                (x8, y8),
                (end_x, end_y),
                (0, 255, 0),
                3
            )
        else:
            cv2.putText(
                img,
                "NOT AIMING",
                (10, 200),
                cv2.FONT_HERSHEY_PLAIN,
                2,
                (0, 0, 255),
                2
            )



        #pinky finger
        x17, y17 = lmList[17][1], lmList[17][2]
        x20, y20 = lmList[20][1], lmList[20][2]

        pinky_length = np.hypot(x20 - x17, y20 - y17)
        pinky_ratio = pinky_length / hand_size

        pinky_extended = pinky_ratio > 0.8

        # print("Pinky ratio:", round(pinky_ratio, 2))
        # print("Pinky:", pinky_extended)

        weapon_armed = index_extended and pinky_extended

        if weapon_armed:
            cv2.putText(
                img,
                "WEB SHOOTER: ARMED",
                (10, 120),
                cv2.FONT_HERSHEY_PLAIN,
                2,
                (0, 255, 0),
                2
            )
        else:
            cv2.putText(
                img,
                "WEB SHOOTER: DISARMED",
                (10, 120),
                cv2.FONT_HERSHEY_PLAIN,
                2,
                (0, 255, 0),
                2
            )

        #thumb finger
        x2, y2 = lmList[2][1], lmList[2][2]
        x4, y4 = lmList[4][1], lmList[4][2]

        thumb_length = np.hypot(x4 - x2, y4 - y2)
        thumb_ratio = thumb_length / hand_size
        thumb_to_pinky = np.hypot(x4 - x20,y4 - y20)

        thumb_pinky_ratio = thumb_to_pinky / hand_size
        thumb_extended = thumb_pinky_ratio > 2.0

        fire = weapon_armed and thumb_extended and not previous_thumb
        previous_thumb = thumb_extended

        if fire:
            cv2.putText(img,"FIRE!",(10, 300),cv2.FONT_HERSHEY_PLAIN,2,(255, 0, 0),2)
            print("FIRE!")

            web_active = True
            web_splatter = False
            web_distance = 0

            #fixing the origin of firing...it doesnot move if index moves away
            web_start_x = x8
            web_start_y = y8

            #saving the direction of the web projectile based on the index finger direction at the time of firing. 
            length = np.hypot(dx, dy)
            web_dx = dx / length
            web_dy = dy / length

        if web_active:

            web_distance += web_speed

            #how the web projectile progresses
            web_x = int(web_start_x + web_dx * web_distance)
            web_y = int(web_start_y + web_dy * web_distance)

            if web_distance > 500:
                web_active = False

                web_splatter = True
                web_splatter_x = web_x
                web_splatter_y = web_y
                web_splatter_timer = 90 #means ~1 to 2 sec depending on the fps(generally 30-60fps)

            else:
                cv2.circle(img,(web_x, web_y),10,(255, 255, 255),cv2.FILLED)

        if web_splatter:
            # # Draw web splatter
            # cv2.circle(img, (web_splatter_x, web_splatter_y), 25, (255,255,255), 2)
            # cv2.circle(img, (web_splatter_x, web_splatter_y), 15, (255,255,255), 2)

            web_h, web_w = web_image.shape[:2] #get the first 2 values i.e the height and width of the image from the tuple of (h,w,a)
            web_x = web_splatter_x - web_w // 2 
            web_y = web_splatter_y - web_h // 2 #web_splatter_x and y represents the centre of the impact but whn opencv overlays an img it get hold of the top left corner of the img so divide the web image pixels by 2 to get the centre
            img = overlay_image(img, web_image, web_x, web_y)

            print(web_splatter_x, web_splatter_y)
            # Reset after some time
            web_splatter_timer -= 1

            if web_splatter_timer <= 0:
                web_splatter = False
                

            



        # print("Thumb:", round(thumb_pinky_ratio, 2))
        # print("Thumb extended:", thumb_extended)
        # print("Thumb-Pinky:", int(thumb_to_pinky))
        # thumb_length = np.hypot(x4 - x2, y4 - y2)
        # thumb_to_index = np.hypot(
        #     x4 - x8,
        #     y4 - y8
        # )

        # thumb_to_pinky = np.hypot(
        #     x4 - x20,
        #     y4 - y20
        # )

        # print(
        #     "Thumb:", round(thumb_length / hand_size, 2),
        #     "Thumb-Index:", int(thumb_to_index),
        #     "Thumb-Pinky:", int(thumb_to_pinky)
        # )



    cv2.imshow("Virtual Web Shooter", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()