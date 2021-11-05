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

import angles

def frame_add_crosshairs(frame,
                         x,
                         y,
                         r=20,
                         lc=(0, 0, 255),
                         cc=(0, 0, 255),
                         lw=2,
                         cw=1):

    x = int(round(x, 0))
    y = int(round(y, 0))
    r = int(round(r, 0))

    cv2.line(frame, (x, y-r*2), (x, y+r*2), lc, lw)
    cv2.line(frame, (x-r*2, y), (x+r*2, y), lc, lw)

    cv2.circle(frame, (x, y), r, cc, cw)


def main():

    try:

        # ------------------------------
        # set up cameras
        # ------------------------------

        # cameras variables:
        # Aquí se pone el numero del device obtenido en linux: Para obtener este
        # número se obtiene con la siguiente línea de comandos:
        # $ v4l2-ctl --list-devices
        # Tambíen se puede poner un path + filename de un archivo de video, 
        left_camera_source =  './videos/demo_logi-c920-stereo-left-1024x0576-.mp4' #'demo_logi-c920-stereo-left-1280x0720-.mp4'   #./demo_logi-c920-stereo-left-1024x0576-.mp4'  # Left Camera in Camrea Point of View (PoV)
        right_camera_source = './videos/demo_logi-c920-stereo-right-1024x0576-.mp4' #'demo_logi-c920-stereo-right-1280x0720-.mp4'  #./demo_logi-c920-stereo-right-1024x0576-.mp4' # Right Camera in Camrea Point of View (PoV)
        
        # En el caso de utilizar este programa con entradas de archivos de
        # video, el formato de la entrada debe coincidir exactamente con los
        # parámetros de abajo, en este caso, el video tiene 1024x576
        pixel_width = 1024 # 640 # 1280
        pixel_height = 576 # 360 # 720

        # FPS
        frame_rate = 30

        # Set the relative position of the stereocam
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
            print('L:NOT AVAILABLE')
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


        left_detector = handdetector.HandDetector(staticImageMode=False,
                                                  maxHands=2,
                                                  detectionCon=0.65,
                                                  trackCon=0.65,
                                                  img_width=pixel_width,
                                                  img_height=pixel_height)
        right_detector = handdetector.HandDetector(staticImageMode=False,
                                                   maxHands=2,
                                                   detectionCon=0.65,
                                                   trackCon=0.65,
                                                   img_width=pixel_width,
                                                   img_height=pixel_height)

        # ------------------------------
        # stabilize
        # ------------------------------
        time.sleep(0.5)


        # ------------------------------
        # set up angles
        # ------------------------------
        
        # Setup angles
        camera_separation = 13.9 # cms

        # Logi C920s HD Pro Webcam
        camera_hFoV = 70.42  # Horizontal Field of View
        camera_vFoV = 43.3   # Vertical Field of View
        hFoV_angle_rectification = 11.0 # Field of View (FoV) rectifcation
        vFoV_angle_rectification = \
            camera_vFoV * hFoV_angle_rectification/camera_hFoV

        angle_width = camera_hFoV - hFoV_angle_rectification
        angle_height = camera_vFoV - vFoV_angle_rectification
        
        # cameras are the same, so only 1 needed
        angler = angles.Frame_Angles(pixel_width, pixel_height, angle_width,
                                     angle_height)
        angler.build_frame()

        # Index finger tip position
        # ------------------------------
        x_left_finger_screen_pos = 0
        y_left_finger_screen_pos = 0

        # last positive target
        # from camera baseline midpoint
        X, Y, Z, D, = 0, 0, 0, 0
        delta_y = 0


        # Ciclo
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

            hands_left_image = fingers_left_image = []
            hands_right_image = fingers_right_image = []

            # Detect Hands
            if left_detector.findHands(frame_left):
                left_detector.drawHands(frame_left)
                left_detector.drawTips(frame_left)
                
                hands_left_image, fingers_left_image = \
                    left_detector.getFingerTipsPos()

            if right_detector.findHands(frame_right):
                #vk_right.draw_virtual_keyboard(frame_right)
                right_detector.drawHands(frame_right)
                right_detector.drawTips(frame_right)

                hands_right_image, fingers_right_image = \
                    right_detector.getFingerTipsPos()

            # TODO: Validar que en la imagen izquierda exista la mano 
            # izquierda con los dedos izquierdos en relación con la imagen 
            # derecha, es decir, que exista cada mano (izq con izq y derecha
            # con derecha) en ambos frames. Esto porque se puede dar el caso en
            # que en el frame izquierdo exista, por ejemplo, solo la mano
            # derecha y que en el frame derecho exista solo la mano izquierda

            # check 1: fingers in both frames:
            if (len(fingers_left_image) > 0 and len(fingers_right_image) > 0):

                # TODO:  Aquí falta identificar en forma correcta cuando 
                # es la mano izquierda o derecha
                for finger_left, finger_right in \
                    zip(fingers_left_image, fingers_right_image):
                    print('finger_left:{}'.format(finger_left))
                    # print('finger_right:{}'.format(finger_right))

                    # get angles from camera centers
                    xlangle, ylangle = angler.angles_from_center(
                        x = finger_left[2], y = finger_left[3],
                        top_left=True, degrees=True)
                    xrangle, yrangle = angler.angles_from_center(
                        x = finger_right[2], y = finger_right[3],
                        top_left=True, degrees=True)

                    # triangulate
                    X_local, Y_local, Z_local, D_local = angler.location(
                        camera_separation,
                        (xlangle, ylangle),
                        (xrangle, yrangle),
                        center=True,
                        degrees=True)
                    # angle normalization
                    delta_y = 0.006509695290859 * X_local * X_local + \
                        0.039473684210526 * -1 * X_local # + vkb_center_point_camera_dist

                    print('finger_left:{}'.format(finger_left))
                    if finger_left[0] == 0 and finger_left[1] == left_detector.mpHands.HandLandmark.INDEX_FINGER_TIP:
                        x_left_finger_screen_pos =  finger_left[2]
                        y_left_finger_screen_pos = finger_left[3]
                        X = X_local
                        Y = Y_local
                        Z = Z_local
                        D = D_local


            # display camera centers
            angler.frame_add_crosshairs(frame_left)
            angler.frame_add_crosshairs(frame_right)

            frame_add_crosshairs(frame_left, x_left_finger_screen_pos, y_left_finger_screen_pos, 24)
            # Display dashboard
            if display_dashboard:
                # Display dashboard data
                fps1 = int(cam_left.current_frame_rate)
                fps2 = int(cam_right.current_frame_rate)
                cps_avg = int(toolbox.round_half_up(fps))  # Average Cycles per second
                
                text = 'X: {:3.1f}\nY: {:3.1f}\nZ: {:3.1f}\nD: {:3.1f}\nDr:{:3.1f}\nFPS:{}/{}\nCPS:{}'.format(X, Y, Z, D, D-delta_y, fps1, fps2, cps_avg)
                
                lineloc = 0
                lineheight = 30
                for t in text.split('\n'):
                    lineloc += lineheight
                    cv2.putText(frame_left,
                                t,
                                (10, lineloc),              # location
                                cv2.FONT_HERSHEY_PLAIN,     # font
                                1.5,                        # size
                                (0, 255, 0),                # color
                                2,                          # line width
                                cv2.LINE_AA,
                                False)


            # Display frames
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
