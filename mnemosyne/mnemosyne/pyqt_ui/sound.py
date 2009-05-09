#
# sound.py <Peter.Bienstman@UGent.be>, Laurent Mauron
#

from PyQt4.phonon import Phonon

from mnemosyne.libmnemosyne.filter import Filter


class SoundManager:
    
    """Wrapper class to play sound files using then Phonon library."""
    
    def __init__(self):
        self.music = None 
        pass

    def play(self, filename):
        if not self.music:
            self.music = Phonon.createPlayer(Phonon.MusicCategory)

        if self.music.state == Phonon.PlayingState:
            self.music.enqueue(filename)
        else:
            self.music.enqueue(Phonon.MediaSource(filename));
            self.music.play()

soundmanager = SoundManager()


class SoundPlayer(Filter):

    def run(self, text, fact):
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
        return text


