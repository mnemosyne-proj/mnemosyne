#
# test_filter.py <Peter.Bienstman@UGent.be>
#

import subprocess as sp

from pytest import raises
from unittest import mock

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne.filter import Filter
from mnemosyne.libmnemosyne.filters.html5_video import Html5Video
from mnemosyne.libmnemosyne.filters.html5_audio import Html5Audio
from mnemosyne.libmnemosyne.filters.RTL_handler import RTLHandler
from mnemosyne.libmnemosyne.filters.expand_paths import ExpandPaths
from mnemosyne.libmnemosyne.filters.escape_to_html import EscapeToHtml
from mnemosyne.libmnemosyne.filters.latex import CheckForUpdatedLatexFiles, Latex

side_effects = [FileNotFoundError, sp.TimeoutExpired(cmd='foo', timeout=5),
                sp.CalledProcessError(cmd='foo', returncode=1)]
check_output_mock = mock.Mock(side_effect=side_effects)
check_call_mock = mock.Mock(side_effect=side_effects)

class TestFilter(MnemosyneTest):

    def test(self):
        with raises(NotImplementedError):
            f = Filter(None)
            f.run("", None, None)

    def test_html5_audio(self):

        f = Html5Audio(self.mnemosyne.component_manager)

        self.config()["media_autoplay"] = True
        self.config()["media_controls"] = True

        f.run("""<audio src="b">""", None, None)

        self.config()["media_autoplay"] = False
        self.config()["media_controls"] = True

        f.run("""<audio src="b">""", None, None)

    def test_html5_video(self):

        f = Html5Video(self.mnemosyne.component_manager)

        self.config()["media_autoplay"] = True
        self.config()["media_controls"] = True

        assert f.run("""<video src="b">""", None, None) == \
              """<video src="b" autoplay=1 controls=1>"""

        self.config()["media_autoplay"] = False
        self.config()["media_controls"] = True

        assert f.run("""<video src="b">""", None, None) == \
              """<video src="b" controls=1>"""

    def test_escape_to_html(self):

         f = EscapeToHtml(self.mnemosyne.component_manager)

         assert f.run("a\nb", None, None) == "a<br>b"
         assert f.run("<latex>a\nb<\latex>", None, None) == "<latex>a\nb<\latex>"
         
    def test_expand_paths(self):

        f = ExpandPaths(self.mnemosyne.component_manager)
         
        assert "media" not in \
               f.run("""data=trainingData, method=\"rpart\"""", None, None)
        assert "media" in \
               f.run("""data=\"rpart\"""", None, None)
        assert "media" in \
               f.run("""data= \"rpart\"""", None, None)        
        assert "media" not in \
               f.run("""Application data = \"rpart\"""", None, None) 
        
    def test_RTL_handler(self):

        f = RTLHandler(self.mnemosyne.component_manager)

        f.run(chr(0x0591), None, None)
        f.run(chr(0x0491), None, None)
        f.run("[a]" + chr(0x0491), None, None)


    @mock.patch('mnemosyne.libmnemosyne.filters.latex.sp.check_output',
                check_output_mock)
    @mock.patch('mnemosyne.libmnemosyne.filters.latex.sp.check_call',
                check_call_mock)
    def test_latex_exceptions(self):
        for _ in side_effects:
            f = CheckForUpdatedLatexFiles(self.mnemosyne.component_manager)
            assert f.is_working() is False

            f = Latex(self.mnemosyne.component_manager)
            # Should not raise an exception
            f._call_cmd(['dummy', 'cmd'],
                        'dot_test/default.db_media/latex_out.txt')
