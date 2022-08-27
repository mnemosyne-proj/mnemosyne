#
# audio_player_container.py
#

# Is needed for JavaScript generation.
# Contains the ID's of HTML audioplayers.
# For example the ID "b" of the player
# <audio id="b" controls><source src="one.mp3"><source src="two.mp3"></audio>
# is stored in the member variable players.
class AudioPlayerContainer:
    def __init__(self):
        self.players = [] 
