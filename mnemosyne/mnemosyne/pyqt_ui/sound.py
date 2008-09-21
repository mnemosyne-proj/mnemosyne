from PyQt4.phonon import Phonon

class SoundManager:
    '''Wrapper class to play sound files using phonon library'''
    def __init__(self):
        self.music = None 
        pass

    def play(self, filename):
        if not self.music:
            self.music = Phonon.createPlayer(Phonon.MusicCategory)

        if self.music.state == Phonon.PlayingState:
            self.music.enqueue(filename)
        else:
            self.music.enqueue(Phonon.MediaSource(fn));
            self.music.play()

soundmanager = SoundManager()

def play_sound(text):
    """find <sound> html elements in text and play file specified by src attribute"""
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
