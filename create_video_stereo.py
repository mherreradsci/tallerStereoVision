#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  2 13:19:00 2021
Test de video thread
@author: mherrera
"""


# import sys
import cv2
import video_thread as video_thread
import math
import time

import traceback

import screen_tools as st

def round_half_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n*multiplier + 0.5) / multiplier

# @staticmethod
def open_output_stream(path='', video_fourcc = cv2.VideoWriter.fourcc(*'mp4v'), fps=0, frame_size=(640, 480)):
    output_stream = None
    if path:
        output_stream = cv2.VideoWriter(
            path,
            video_fourcc, fps, frame_size)
    return output_stream


def main():
    try:
        print('Inicio')
       
        cameras_id = {
            'logi-c920-stereo-left': 2,
            'logi-c920-stereo-right': 0,
            #'countdown 10': '/home/mherrera/Proyectos/Desa/00400-VirtualPianoKeyboard/1100-Integracion/virtualpiano/resources/stock-footage-old-film-style-seconds-countdown.webm',
            #'file1': '/home/mherrera/Videos/demo1video-live.mp4',
            #'file2': '/home/mherrera/Videos/demo1video-live.mp4',
            # 'stream': 'rtsp://mherrera:Treka2021x.p@192.168.0.80/videoMain'
            # 'FaceCam 1000X': 4,
            # 'built-in cam nitro': 6,
            # 'jetson-nano-rbp-v2': 'rtsp://192.168.0.60:8554/test',
            # 'jetson-nano-rbp-v2-ir': 'rtsp://192.168.0.60:8555/test',
            # 'foscam-ir-loopback':12,  # ffmpeg loopback
            #'foscam-ip': 'rtsp://mherrera:'+password+'@192.168.0.80/videoMain',
        }

        print('cameras_id:{}'.format(cameras_id))

        screen = st.ScreenTools()
        screen_w, screen_h = screen.screen_size()
        print('screen size:(WxH): {}x{}'.format(screen_w, screen_h))

        # cameras variables
        pixel_width =  1024 # 640 # 1280  # 1024 # 1280 # 640  # 352 # 640
        pixel_height = 576 # 360 # 720  # 576 #  720 # 360  # 288 # 360
        frame_rate = 15 # FPS
        
        #video_fourcc=cv2.VideoWriter_fourcc(*"mjpg")
        video_fourcc=cv2.VideoWriter.fourcc(*'mp4v')

        cameras_list = []
        output_list = []
        windows_names = []
        for i, (name, c_id) in enumerate(cameras_id.items()):
            cam_resource = video_thread.VideoThread(
                video_source=c_id,
                video_width=pixel_width,
                video_height=pixel_height,
                video_frame_rate=frame_rate,
                buffer_all=False,
                video_fourcc = video_fourcc,
                try_to_reconnect=False
            )
            cameras_list.append(cam_resource)
            w_name = 'cam:{} - {}'.format(i, name)
            
            windows_names.append(w_name)
            cam_resource.start()

            if cam_resource.is_available():
                # Output
                output_filename='demo_{}-{:04}x{:04}-{}'.format(name, pixel_width, pixel_height, '.mp4') # 'mjpeg'
                output= open_output_stream(
                    path=output_filename,
                    video_fourcc = video_fourcc,
                    fps=frame_rate, 
                    frame_size=(pixel_width, pixel_height)
                    )

                output_list.append(output)
                print('Name:{}'.format(w_name))
                print('cam_resource.resource.get(cv2.CAP_PROP_AUTO_EXPOSURE:{}'.
                      format(cam_resource.resource.get(cv2.CAP_PROP_AUTO_EXPOSURE)))
                print('cam_resource.resource.get(cv2.CAP_PROP_EXPOSURE:{}'.
                      format(cam_resource.resource.get(cv2.CAP_PROP_EXPOSURE)))
                print('cam_resource.resource.get(cv2.CAP_PROP_AUTOFOCUS):{}'.
                      format(cam_resource.resource.get(cv2.CAP_PROP_AUTOFOCUS)))
                print('cam_resource.resource.get(cv2.CAP_PROP_BUFFERSIZE):{}'.
                      format(cam_resource.resource.get(cv2.CAP_PROP_BUFFERSIZE)))
                print('cam_resource.resource.get(cv2.CAP_PROP_CODEC_PIXEL_FORMAT):{}'.
                      format(cam_resource.resource.get(cv2.CAP_PROP_CODEC_PIXEL_FORMAT)))

                print('cam_resource.resource.get(cv2.CAP_PROP_HW_DEVICE):{}'.
                      format(cam_resource.resource.get(cv2.CAP_PROP_HW_DEVICE)))
                print('cam_resource.resource.get(cv2.CAP_PROP_FRAME_COUNT):{:03f}'.
                      format(cam_resource.resource.get(cv2.CAP_PROP_FRAME_COUNT)))
                

        # Arrange im windows

        # imshow dims
        imw_width = 640
        imw_height = 288

        w_cols = screen_w // imw_width
        # w_rows = screen_h // imw_height
        start_x, start_y = 70, 60 # Descktop Ubuntu 18 - gnome Desktop

        row = 0
        for i, w_name in enumerate(windows_names):
            cv2.namedWindow(w_name, cv2.WINDOW_NORMAL)
            cv2.setWindowProperty(w_name,
                                  cv2.WND_PROP_FULLSCREEN,
                                  cv2.WINDOW_FULLSCREEN)
            cv2.resizeWindow(w_name, imw_width, imw_height)
            col = (i % w_cols)

            x_pos = imw_width * col + 1
            y_pos = int(imw_height * 1.15) * row
            
            cv2.moveWindow(w_name,
                           start_x + x_pos,
                           start_y + y_pos,
                           )
            
            
            if col == w_cols-1:
                row = row + 1

        # # Output both videos
        # left_output= open_output_stream(
        #     path='demo_both_c920.mp4', # 'mjpeg',
        #     video_fourcc = video_fourcc,
        #     fps=frame_rate, 
        #     frame_size=(pixel_width, pixel_height)
        #     )


        start = time.time()
        cycles = 0
        cps = 0

        display_dashboard = True
        while True:
            cycles += 1
            # get frames
            for cam_resource, out_resource, window_name in zip(cameras_list, output_list, windows_names):
                finished, frame = cam_resource.next(black=True, wait=0.5)
                if not finished:
                    if display_dashboard:
                        cam_FPS = round_half_up(cam_resource.current_frame_rate)
        
                        start_x_y_pos = (20, 40)
                        cv2.putText(frame, f'FPS: {cam_FPS:3.2f} CPS: {cps:03.02f}',
                                    start_x_y_pos,
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
                        start_x_y_pos = (20, 80)
                        cv2.putText(frame, 'cam conf: W:{} - H:{} - FPS:{:3.2f}'.
                                    format(cam_resource.get_curr_config_widht(),
                                           cam_resource.get_curr_config_height(),
                                           cam_resource.get_curr_config_fps()),
                                    start_x_y_pos,
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    
                    cv2.imshow(window_name, frame)
                    out_resource.write(frame)

            # Process
            # frame_cam_1 =  cv2.rotate(src=frame_cam_1, rotateCode=cv2.ROTATE_180)

            if cycles % 10 == 0:
                end = time.time()
                totalTime = end - start
                cps = round(10 / totalTime, 2)
                start = time.time()

            # if cycles % 10 == 0:
            #     print('threading.active_count():{}'.format(threading.active_count()))

            # Hit "q" to close the window
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q') or len(cameras_list) == 0:
                break
            elif key == ord('d'):
                if display_dashboard:
                    display_dashboard = False
                else:
                    display_dashboard = True            

    # ------------------------------
    # full error catch
    # ------------------------------
    except:
        print('[ERROR]:' + traceback.format_exc())

    finally:
        # Release and destroy all windows before termination
        # ------------------------------
        # close all
        # ------------------------------
        for cam_resource in cameras_list:
            try:
                cam_resource.stop()
            except Exception:
                pass

        for out_resource in output_list:
            try:
                out_resource.release()
            except Exception:
                print('Eroaaaaaarssss')
                pass



        cv2.destroyAllWindows()
        #left_output.release()

if __name__ == "__main__":
    main()
