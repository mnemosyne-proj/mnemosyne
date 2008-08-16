##############################################################################
#
# Sound support through pygame and SDL <Peter.Bienstman@UGent.be>
#
##############################################################################

import pygame

##############################################################################
#
# SoundManager
#
#  pygame only allows queuing a single sound at a time, so we write some
#  extra queuing code around it.
#  The update function needs to be called regularly, e.g. from a repeating
#  timer in the GUI.
#
##############################################################################

class SoundManager:

    def __init__(self):

        self.queue = []

    def play(self, filename):

        if pygame.mixer.music.get_busy():
            self.queue.append(filename)
        else:
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()

    def update(self):

        if len(self.queue) != 0 and not pygame.mixer.music.get_busy():
            filename = self.queue.pop(0)
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()

soundmanager = SoundManager()



##############################################################################
#
# play_sound
#
#  Extract path from a <sound src=".."> tag and play it.
#
##############################################################################

def play_sound(text):

    i = text.lower().find("sound src")
    
    while i != -1:
        
        start = text.find("\"", i)
        end   = text.find("\"", start+1)

        if end == -1:
            return

        filename = text[start+1:end]
        try:
            soundmanager.play(filename)
        except:
            print "Unable to play music from file", filename

        i = text.lower().find("sound src", i+1)    
            
