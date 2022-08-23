#
# multiple_audiofile_support.py
#

from mnemosyne.web_server.audio_player_container import AudioPlayerContainer

# Global object for code optimization.
# Is used for JavaScript generation.
# Contains the ID's of HTML audioplayers.
ap_container = AudioPlayerContainer() 

# Contains the ID of a HTML audioplayer.
# Is used for JavaScript generation.
class AudioPlayer:
     def __init__(self, id):
        self.id = id

# Inserts html audio tags.
# For example <source src='soundfile.mp3'> becomes  
# <audio id='player_b' controls><source src='soundfile.mp3'></audio>.
class InsertAudioplayerTags:
    def __init__(self, audio_files_counter):
        self.__audio_files_counter = audio_files_counter
        self.players = []    
    def insert_audioplayer_tags(self, text, fact_key):
        str1 = '<audio id="player_{id}" controls>\n' \
                    .format(id = fact_key)
        str2 = '</audio>' 
        index = text.find('<source src=')
        text_audioplayer_inserted = text[:index] + str1 + text[index:]
        text_audioplayer_inserted += str2
        if self.__audio_files_counter > 1:
            # Player has to play >1 file, JavaScript will be inserted.
            player = AudioPlayer(fact_key)
            ap_container.players.append(player)
        return text_audioplayer_inserted


# Inserts JavaScript into the HTML page when an audio player needs to play more 
# than one sound file. For example the audio player with the id "b" has to play
# two sound files. 
# <audio id="b" controls><source src="one.mp3"><source src="two.mp3"></audio>
# So, JavaScript will be added to the page,
# to enable the ability playing both files.
class InsertJavascript:
    def __del__(self):
        ap_container.players.clear() # Reset content for the next page.
    # Inserts JavaScript into the html page :-O            
    def insert_javascript(self, html_page):
        if 1 < len(ap_container.players):
            # Return unchanged page, no need to insert JavaScript
            return html_page 
        # Contains two lines of JavaScript for each audio player.
        # For example
        # var audio_player_b = null;
        # let index_b = { val : 0 }; 
        audio_player_with_index = ""
        # Contains a JavaScript funtion call to initialize 
        # and to start the audio player.
        # For example
        # init_player(audio_player_b, 'player_b', index_b); 
        call_init_player = ""
        for player in ap_container.players: 
            audio_player_with_index += \
                'var audio_player_{id} = null;\n'.format(id = player.id)
            audio_player_with_index += "let index_{id} = {val};\n". \
                            format(id = player.id, val =  "{val : 0}" )
            call_init_player += \
                "init_player(audio_player_{id}, 'player_{id}' , index_{id});\n".format(id = player.id) 
        javascript = """
            <script>
                %s
                function init_player(audio_player, fact_id, index)
                {
                    var audio_player = document.getElementById(fact_id, index);
                    if (null === audio_player) return;
                        
                    if(audio_player.children.length > 1)  
                    {
                        audio_player.addEventListener('ended', function(event)
                        {
                            play.call(this, event, audio_player, index);
                        }, false);
                    }
                    audio_player.src = audio_player.children[index.val].src
                }
                
                var play = function play_playlist(event, audio_player, index)
                {
                    index.val += 1; 
                    audio_player.autoplay = true;
                    if(index.val == audio_player.children.length)
                    {
                        audio_player.autoplay = false;
                        index.val = 0;
                    }
                    audio_player.src = audio_player.children[index.val].src
                }
                %s   
          </script> 		 
          """ % (audio_player_with_index, call_init_player)
        index = html_page.find(b'</body>')
        if -1 == index:
            return html_page
        html_page_javascript_inserted = (html_page[:index] 
                                            + javascript.encode('utf-8')
                                            + html_page[index:])
        return html_page_javascript_inserted
