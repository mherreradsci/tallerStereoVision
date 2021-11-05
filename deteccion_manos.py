#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  4 02:19:37 2021

@author: mherrera
"""

import handdetector
import video_thread
import toolbox
import time
import cv2
import numpy as np
import traceback

def main():

    try:

        # ------------------------------
        # set up cameras
        # ------------------------------

        # cameras variables
        left_camera_source =  'demo_logi-c920-stereo-left-1024x0576-.mp4' #'demo_logi-c920-stereo-left-1280x0720-.mp4'   #./demo_logi-c920-stereo-left-1024x0576-.mp4'  # Left Camera in Camrea Point of View (PoV)
        right_camera_source = 'demo_logi-c920-stereo-right-1024x0576-.mp4' #'demo_logi-c920-stereo-right-1280x0720-.mp4'  #./demo_logi-c920-stereo-right-1024x0576-.mp4' # Right Camera in Camrea Point of View (PoV)
        pixel_width = 1024 # 640 # 1280
        pixel_height = 576 # 360 # 720


        # FPS
        frame_rate = 15

        camera_in_front_of_you = False

        # left camera 1
        cam_left = video_thread.VideoThread(
            video_source=left_camera_source,
            video_width=pixel_width,
            video_height=pixel_height,
            video_frame_rate=frame_rate,
            buffer_all=True,
            try_to_reconnect=False)

        # right camera 2
        cam_right = video_thread.VideoThread(
            video_source=right_camera_source,
            video_width=pixel_width,
            video_height=pixel_height,
            video_frame_rate=frame_rate,
            buffer_all=True,
            try_to_reconnect=False)

        # start cameras
        cam_left.start()
        cam_right.start()

        time.sleep(1)
        if camera_in_front_of_you:
            main_window_name = 'In fron of you: rigth+left cam'
        else:
            main_window_name = 'Same Point of View: left+rigth cam'

        cv2.namedWindow(main_window_name)
        cv2.moveWindow(main_window_name,
                       (pixel_width//2),
                       (pixel_height//2))        
        
        if cam_left.is_available():
            print('Name:{}'.format(main_window_name))
            print('cam_left.resource.get(cv2.CAP_PROP_AUTO_EXPOSURE:{}'.
                  format(cam_left.resource.get(cv2.CAP_PROP_AUTO_EXPOSURE)))
            print('cam_left.resource.get(cv2.CAP_PROP_EXPOSURE:{}'.
                  format(cam_left.resource.get(cv2.CAP_PROP_EXPOSURE)))
            print('cam_left.resource.get(cv2.CAP_PROP_AUTOFOCUS):{}'.
                  format(cam_left.resource.get(cv2.CAP_PROP_AUTOFOCUS)))
            print('cam_left.resource.get(cv2.CAP_PROP_BUFFERSIZE):{}'.
                  format(cam_left.resource.get(cv2.CAP_PROP_BUFFERSIZE)))
            print('cam_left.resource.get(cv2.CAP_PROP_CODEC_PIXEL_FORMAT):{}'.
                  format(cam_left.resource.get(cv2.CAP_PROP_CODEC_PIXEL_FORMAT)))

            print('cam_left.resource.get(cv2.CAP_PROP_HW_DEVICE):{}'.
                  format(cam_left.resource.get(cv2.CAP_PROP_HW_DEVICE)))
            print('cam_left.resource.get(cv2.CAP_PROP_FRAME_COUNT):{:03f}'.
                  format(cam_left.resource.get(cv2.CAP_PROP_FRAME_COUNT)))
        else:
            print('NOT AVAILABLE')
            return
                

        if cam_right.is_available():
            print('Name:{}'.format(main_window_name))
            print('cam_right.resource.get(cv2.CAP_PROP_AUTO_EXPOSURE:{}'.
                  format(cam_right.resource.get(cv2.CAP_PROP_AUTO_EXPOSURE)))
            print('cam_right.resource.get(cv2.CAP_PROP_EXPOSURE:{}'.
                  format(cam_right.resource.get(cv2.CAP_PROP_EXPOSURE)))
            print('cam_right.resource.get(cv2.CAP_PROP_AUTOFOCUS):{}'.
                  format(cam_right.resource.get(cv2.CAP_PROP_AUTOFOCUS)))
            print('cam_right.resource.get(cv2.CAP_PROP_BUFFERSIZE):{}'.
                  format(cam_right.resource.get(cv2.CAP_PROP_BUFFERSIZE)))
            print('cam_right.resource.get(cv2.CAP_PROP_CODEC_PIXEL_FORMAT):{}'.
                  format(cam_right.resource.get(cv2.CAP_PROP_CODEC_PIXEL_FORMAT)))

            print('cam_right.resource.get(cv2.CAP_PROP_HW_DEVICE):{}'.
                  format(cam_right.resource.get(cv2.CAP_PROP_HW_DEVICE)))
            print('cam_right.resource.get(cv2.CAP_PROP_FRAME_COUNT):{:03f}'.
                  format(cam_right.resource.get(cv2.CAP_PROP_FRAME_COUNT)))


        # left_window_name = 'frame left'
        # cv2.namedWindow(left_window_name)
        # cv2.moveWindow(left_window_name,
        #                (pixel_width//2),
        #                (pixel_height//2))

        # right_window_name = 'frame right'
        # cv2.namedWindow(right_window_name)
        # cv2.moveWindow(right_window_name,
        #                (pixel_width//2)+640,
        #                (pixel_height//2))





        left_detector = handdetector.HandDetector(staticImageMode=False,
                                                  maxHands=2,
                                                  detectionCon=0.65,
                                                  trackCon=0.65,
                                                  img_width=pixel_width,
                                                  img_height=pixel_height)
        right_detector = handdetector.HandDetector(staticImageMode=False,
                                                   detectionCon=0.65,
                                                   trackCon=0.65,
                                                   img_width=pixel_width,
                                                   img_height=pixel_height)



        # variables
        # ------------------------------

        
        cycles = 0
        fps = 0
        start = time.time()
        display_dashboard = True
        while cam_left.is_available() and cam_right.is_available():
            cycles += 1
            # get frames
            finished_left, frame_left = cam_left.next(black=True, wait=0.5)
            finished_right, frame_right = cam_right.next(black=True, wait=0.5)

            if camera_in_front_of_you:
                frame_left = cv2.flip(frame_left, -1)  # Selfie point of view
                frame_right = cv2.flip(frame_right, -1)  # Selfie point of view

            hands_on_left_image = fingers_on_left_image = []
            hands_on_right_image = fingers_on_right_image = []

            # Detect Hands
            if left_detector.findHands(frame_left):
                left_detector.drawHands(frame_left)
                left_detector.drawTips(frame_left)
                
                hands_on_left_image, fingers_on_left_image = \
                    left_detector.getFingerTipsPos()

            if right_detector.findHands(frame_right):
                #vk_right.draw_virtual_keyboard(frame_right)
                right_detector.drawHands(frame_right)
                right_detector.drawTips(frame_right)

                hands_on_right_image, fingers_on_right_image = \
                    right_detector.getFingerTipsPos()
            # else:
            #     vk_right.draw_virtual_keyboard(frame_right)

            # TODO: Validar que en la imagen izquierda exista la mano 
            # izquierda con los dedos izquierdos en relación con la imagen 
            # derecha, es decir, que exista cada mano (izq con izq y derecha
            # con derecha) en ambos frames. Esto porque se puede dar el caso en
            # que en el frame izquierdo exista, por ejemplo, solo la mano
            # derecha y que en el frame derecho exista solo la mano izquierda


            # check 1: hands and finges in both frames:
            if (len(fingers_on_left_image) > 0 and len(fingers_on_right_image) > 0):

                for finger_left, finger_right in \
                    zip(fingers_on_left_image, fingers_on_right_image):
                    print('finger_left:{}'.format(finger_left))
                    # print('finger_right:{}'.format(finger_right))
                    # get angles from camera centers
                    # angle normalization


            # display camera centers

            if display_dashboard:
                # Display dashboard data
                fps1 = int(cam_left.current_frame_rate)
                fps2 = int(cam_right.current_frame_rate)
                cps_avg = int(toolbox.round_half_up(fps))  # Average Cycles per second
                text = 'FPS:{}/{}\nCPS:{}'.format(fps1, fps2, cps_avg)
                lineloc = 0
                lineheight = 30
                for t in text.split('\n'):
                    lineloc += lineheight
                    cv2.putText(frame_left,
                                t,
                                (10, lineloc),              # location
                                cv2.FONT_HERSHEY_PLAIN,     # font
                                # cv2.FONT_HERSHEY_SIMPLEX, # font
                                1.5,                        # size
                                (0, 255, 0),                # color
                                2,                          # line width
                                cv2.LINE_AA,
                                False)

            # Display current target
            # if fingers_left_queue:
            #     frame_add_crosshairs(frame_left, x1m, y1m, 24)
            #     frame_add_crosshairs(frame_right, x2m, y2m, 24)

            # if fingers_left_queue:
            #     frame_add_crosshairs(frame_left, x1m, y1m, 24)
            #     frame_add_crosshairs(frame_right, x2m, y2m, 24)
            # if X > 0 and Y > 0:
#            frame_add_crosshairs(frame_left, x_left_finger_screen_pos, y_left_finger_screen_pos, 24)
            # Pendiente : ...frame_add_crosshairs(frame_right, x_left_finger_screen_pos, y_left_finger_screen_pos, 24)



            # Display frames

            # cv2.imshow(left_window_name, frame_left)
            # cv2.imshow(right_window_name, frame_right)

            if camera_in_front_of_you:
                h_frames = np.concatenate((frame_right, frame_left), axis=1)
            else:
                h_frames = np.concatenate((frame_left, frame_right), axis=1)

            cv2.imshow(main_window_name, h_frames)



            if (cycles % 10 == 0):
                # End time
                end = time.time()
                # Time elapsed
                seconds = end - start
                # print ("Time taken : {0} seconds".format(seconds))
                # Calculate frames per second
                fps = 10 / seconds
                start = time.time()

            # Detect control keys
            key = cv2.waitKey(1) & 0xFF
            if cv2.getWindowProperty(
                    main_window_name, cv2.WND_PROP_VISIBLE) < 1:
                break
            # elif cv2.getWindowProperty(
            #         right_window_name, cv2.WND_PROP_VISIBLE) < 1:
            #     break
            elif key == ord('q'):
                break
            elif key == ord('d'):
                if display_dashboard:
                    display_dashboard = False
                else:
                    display_dashboard = True
            elif key != 255:
                print('KEY PRESS:', [chr(key)])

    # ------------------------------
    # full error catch
    # ------------------------------
    except Exception:
        print(traceback.format_exc())

    # ------------------------------
    # close all
    # ------------------------------

    # close camera1
    try:
        cam_left.stop()
    except Exception:
        pass

    # close camera2
    try:
        cam_right.stop()
    except Exception:
        pass

    # kill frames
    cv2.destroyAllWindows()

    # done
    print('DONE')


# ------------------------------
# Call to Main
# ------------------------------

if __name__ == '__main__':
    main()
