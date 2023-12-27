import vlc
import time
import sys

media_player = vlc.MediaPlayer()

# media object 
media = vlc.Media(sys.argv[1]) 
  
# setting media to the media player 
media_player.set_media(media) 
  
  
  
# start playing video + commenting it  
media_player.play() 
time.sleep(2)
# wait for it to load
# checking if it is playing 
while media_player.is_playing():
    time.sleep(1)