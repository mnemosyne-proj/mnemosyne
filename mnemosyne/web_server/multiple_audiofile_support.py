class InsertJavascript:
    def __init__(self):
        self.__audio_player_has_multiple_files = False
        #var audio_player_f = null;
        #let index_f = { val : 0 }; each song has it's own index
        self.__audio_player_with_index = ""
        #init_player(audio_player_f, 'player_f', index_f);
        self.__call_init_player = ""

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

    def __prepare_javascript(self, html_page):
        fact_keys = ["f", "p_1", "m_1", "n"]
        for key in fact_keys:
            #eg audio_player_tag_in_html_page = <audio id="player_f" controls>
            audio_player_tag = '<audio id="player_{fact_id}" controls>' \
                                    .format(fact_id = key)
            audio_player_tag = bytes(audio_player_tag, encoding='utf-8')
            if True == \
                self. __player_has_multiple_files(audio_player_tag, html_page):
                #current player has more than 1 sound file to play
                self.__audio_player_has_multiple_files = True
                if key == "f":
                    self.__audio_player_with_index \
                        += "var audio_player_f = null;\n"    
                    self.__audio_player_with_index \
                        += "let index_f = { val : 0 };\n"
                    self.__call_init_player += ("init_player(audio_player_f,"
                    "'player_f', index_f);\n")
                elif key == "p_1":
                    self.__audio_player_with_index += \
                        "var audio_player_p_1 = null;\n"
                    self.__audio_player_with_index += \
                        "let index_p_1 = { val : 0 };\n"
                    self.__call_init_player += \
                        ("init_player(audio_player_p_1,"
                        "'player_p_1', index_p_1);\n")
                elif key == "m_1":
                    self.__audio_player_with_index \
                        += "var audio_player_m_1 = null;\n"
                    self.__audio_player_with_index \
                        += "let index_m_1 = { val : 0 };\n"
                    self.__call_init_player \
                        += ("init_player(audio_player_m_1,"
                            "'player_m_1', index_m_1);\n")
                else: #key == "n"
                    self.__audio_player_with_index \
                        += "var audio_player_n = null;\n"
                    self.__audio_player_with_index \
                        += "let index_n = { val : 0 };\n"
                    self.__call_init_player \
                        += ("init_player(audio_player_n,"
                            "'player_n', index_n);\n")

    def insert_javascript(self, html_page):
        self.__prepare_javascript(html_page)
        if False == self.__audio_player_has_multiple_files:
        #html_page comes with audio tags <audio id="player_{fact_id}" controls>
        #audio tags are inerted by method insert_audioplayer_tag
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
        html_page_javascript_inserted = (html_page[:index] 
                                            + javascript.encode('utf-8')
                                            + html_page[index:])
        return html_page_javascript_inserted


class InsertAudioplayerTags:
    def insert_audioplayer_tags(self, text, fact_key):
        str1 = '<audio id="player_{fact_id}" controls>' \
                    .format(fact_id = fact_key)
        str2 = '</audio>' 
        index = text.find('<source src=')
        text_audioplayer_inserted = text[:index] + str1 + text[index:]
        text_audioplayer_inserted += str2    
        return text_audioplayer_inserted
