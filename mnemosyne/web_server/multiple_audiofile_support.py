#
# multiple_audiofile_support.py
#


# Inserts html audio tags.
# For example <source src='soundfile.mp3'> becomes  
# <audio id='player_b' controls><source src='soundfile.mp3'></audio>.

class InsertAudioplayerTags:
    def insert_audioplayer_tags(self, text, fact_key):
        str1 = '<audio id="player_{id}" controls>\n' \
                    .format(id = fact_key)
        str2 = '</audio>' 
        index = text.find('<source src=')
        text_audioplayer_inserted = text[:index] + str1 + text[index:]
        text_audioplayer_inserted += str2    
        return text_audioplayer_inserted


# Inserts JavaScript into the HTML page when an audio player needs to play more 
# than one sound file. For example the audio player with the id "b" has to play
# two sound files. 
# <audio id="b" controls><source src="one.mp3"><source src="two.mp3"></audio>
# So, JavaScript will be added to the page,
# to enable the ability playing both files.

class InsertJavascript:
    def __init__(self):
        # Becomes True when an audio player needs to play more than one 
        # sound file.        
        self.__audio_player_has_multiple_files = False
        
        # Contains two lines of JavaScript for each audio player.
        # For example
        # var audio_player_b = null;
        # let index_b = { val : 0 }; 
        self.__audio_player_with_index = ""
        
        # Contains a JavaScript funtion call to initialize 
        # and to start the audio player.
        # For example
        # init_player(audio_player_b, 'player_b', index_b); 
        self.__call_init_player = ""

    # Helper method for method __prepare_javascript
    # Returns true if a player has to play more than one file, else
    # false.
    def  __player_has_multiple_files(self, audio_player_tag, html_page):
        start_index = html_page.find(audio_player_tag)
        end_index = -1
        audio_files_count = 0
        if -1 != start_index:
            end_index = html_page.find(b"</audio>", start_index)
        if start_index != -1 and end_index != -1:
            substr = html_page[start_index:end_index]
            audio_files_count = substr.count(b'<source src=')
        return audio_files_count > 1

    # Helper method for method insert_javascript
    # Assembles JavaScript code and stores it in the member variables
    # self.__audio_player_with_index and self.__call_init_player
    def __prepare_javascript(self, html_page):
        fact_keys = ["f", "p_1", "m_1", "n", "b"]
        for key in fact_keys:
            audio_player_tag = '<audio id="player_{fact_id}" controls>' \
                                    .format(fact_id = key)
            audio_player_tag = bytes(audio_player_tag, encoding='utf-8')
            if True == \
                self. __player_has_multiple_files(audio_player_tag, html_page):
                #current player has more than 1 sound file to play
                self.__audio_player_has_multiple_files = True
                text1 = "var audio_player_{id} = null;\n".format(id = 'b')
                text2 = "let index_{id} = {val};\n". \
                            format(id = 'b', val =  "{val : 0}" )
                # All attempts to create a line break resulted in ugly JavaScript results.
                text3 = "init_player(audio_player_{id}, 'player_{id}' , index_{id});\n".format(id = 'b') 
                self.__audio_player_with_index += text1
                self.__audio_player_with_index += text2
                self.__call_init_player += text3

    # Inserts JavaScript into the html page :-O            
    def insert_javascript(self, html_page):
        self.__prepare_javascript(html_page)
        if False == self.__audio_player_has_multiple_files:
            # Return unchanged page, no need to insert JavaScript
            return html_page 
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
          """ % (self.__audio_player_with_index, self.__call_init_player)
        index = html_page.find(b'</body>')
        if -1 == index:
            return html_page
        html_page_javascript_inserted = (html_page[:index] 
                                            + javascript.encode('utf-8')
                                            + html_page[index:])
        return html_page_javascript_inserted
