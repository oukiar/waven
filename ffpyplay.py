
from ffpyplayer.player import MediaPlayer
import time

count = 0

player = MediaPlayer("video1.mp4")
val = ''
while val != 'eof':
    frame, val = player.get_frame()
    if val != 'eof' and frame is not None:
        img, t = frame
        # display img
        print img


        if count == 300:
            break
            
        count += 1

count = 0

player = MediaPlayer("video2.mp4")
val = ''
while val != 'eof':
    frame, val = player.get_frame()
    if val != 'eof' and frame is not None:
        img, t = frame
        # display img
        print img


        if count == 300:
            break
            
        count += 1
