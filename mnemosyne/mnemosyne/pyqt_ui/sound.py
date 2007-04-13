##############################################################################
#
# Sound support through pygame and SDL <Peter.Bienstman@UGent.be>
#
##############################################################################

import pygame

##############################################################################
#
# play_sound
#
#  extract path from a <sound src=".."> tag and play it
#
##############################################################################

def play_sound(text):

    i = text.lower().find("sound src")
    
    if i != -1:
        start = text.find("\"", i)
        end   = text.find("\"", start+1)

        if end == -1:
            return

        filename = text[start+1:end]
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.queue(filename)
            else:
                pygame.mixer.music.load(filename)
                pygame.mixer.music.play()
        except:
            print "Unable to play music from file", filename 
