#
# html5_media.py <Peter.Bienstman@UGent.be>
#

import re

from mnemosyne.libmnemosyne.filter import Filter

re_media = re.compile(r"""<(audio|video)( src=\".+?\")>""", re.DOTALL | re.IGNORECASE)

"""
<script type="text/javascript">

    var soundFiles = new Array('me.mp3', 'yang4.mp3', 'zen3.mp3');
    var next = 0;

    function loadPlayer() {
        var audioPlayer = new Audio();
        audioPlayer.controls = 'controls';
        audioPlayer.addEventListener('ended', nextSoundFile, false);
        document.getElementById('player').appendChild(audioPlayer);
        nextSoundFile();
    }

    function nextSoundFile() {
        var audioPlayer = document.getElementsByTagName('audio')[0];
        if (soundFiles[next] != undefined) {
            audioPlayer.src = soundFiles[next];
            audioPlayer.load();
            audioPlayer.play();
        }
        else {
            // Reset playlist to first sound file.
            next = 0;
            audioPlayer.src = soundFiles[next];
            audioPlayer.load();
        }
        next++;
    }

    window.onload = function() {
        loadPlayer();
    };

</script>

<div id="player"></div>

"""


class Html5Media(Filter):

    """Add autoplay and control tags to html5 media tags."""

    def run(self, text, card, fact_key, **render_args):
        options = ""
        if self.config()["media_autoplay"]:
            options += " autoplay=1"
        if self.config()["media_controls"]:
            options += " controls=1"
        return re.sub(re_media, r"<\1\2" + options + ">", text)


