import vlc

media_player = vlc.MediaPlayer()

# media object 
media = vlc.Media("videos/defend2.mp4") 
  
# setting media to the media player 
media_player.set_media(media) 
  
  
  
# start playing video + commenting it  
media_player.play() 
  
# wait so the video can be played for 5 seconds 
# irrespective of length of video 
time.sleep(5) 
  
# checking if it is playing 
value = media_player.is_playing() 
  
# printing value 
print("Is playing : ") 
print(value) 