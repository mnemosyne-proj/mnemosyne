#
# jquery_mb_html5_audio.py <Peter.Bienstman@gmail.com>
#

import re
import urllib.request, urllib.parse, urllib.error

from mnemosyne.libmnemosyne.filter import Filter

re_audio = re.compile(r"""<audio src=\"(.+?)\"(.*?)>""",
    re.DOTALL | re.IGNORECASE)
re_start = re.compile(r"""start=\"(.+?)\"""",
    re.DOTALL | re.IGNORECASE)
re_stop = re.compile(r"""stop=\"(.+?)\"""",
    re.DOTALL | re.IGNORECASE)


class JQueryMbHtml5Audio(Filter):

    """Audio system based on

    http://pupunzi.open-lab.com/2013/03/13/making-html5-audio-actually-work-on-mobile/

    Issues:

     - only seems to work when loading the info from a webpage and media
       files on disk, not as served through the Mnemosyne web server. Some
       synchronisation issues with the player trying to play the file before
       it's fully ready?
     - need to set an 'end' time which is not beyond the actual end of the
       file, otherwise the file will not play.

    """

    def run(self, text, card, fact_key, **render_args):
        if not re_audio.search(text):
            return text
        sound_files = ""
        play_command = ""
        for match in re_audio.finditer(text):
            filename = urllib.parse.quote(match.group(1).encode("utf-8"), safe="/:")
            id = filename.split(".", 1)[0].replace("/", "")
            start, stop = 0, 2
            if match.group(2):
                start_match = re_start.search(match.group(2))
                if start_match:
                    start = float(start_match.group(1))
                stop_match = re_stop.search(match.group(2))
                if stop_match:
                    stop = float(stop_match.group(1))
            sound_files += """
            %s: {
                id: "%s",
                mp3: "%s",
                sprite: {
                    snippet : {id: "snippet", start: %d, end: %d, loop: false},
                }
            },
            """ % (id, id, filename, start, stop)
            play_command += """$.mbAudio.queue.add(""" + '\"' + id + '\"' + ""","snippet");"""
            text = text.replace(match.group(0), "")
        text = """
<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.9.0/jquery.min.js"></script>
<script type="text/javascript" src="http://pupunzi.github.io/jquery.mb.audio/inc/jquery.mb.audio.js?_=8y338"></script>
<script type="text/javascript">

        $.mbAudio.sounds = {
""" + sound_files + """
        };

function loadPlayer() {
""" + play_command + """
    }

window.onload = function() {
        loadPlayer();
        }
</script>

<button onclick="loadPlayer()">Play</button>  """ + text
        return text
