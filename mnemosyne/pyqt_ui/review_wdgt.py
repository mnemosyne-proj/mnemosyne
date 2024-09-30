#
# review_wdgt.py <Peter.Bienstman@gmail.com>
#

import os

from PyQt6 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.pyqt_ui.ui_review_wdgt import Ui_ReviewWdgt
from mnemosyne.libmnemosyne.ui_components.review_widget import ReviewWidget


class QAOptimalSplit(object):

    """Algorithm to make sure the split between question and answer boxes is
    as optimal as possible.

    This code is not part of ReviewWidget, in order to be able to reuse this
    in Preview Cards.

    """

    used_for_reviewing = True

    def __init__(self, **kwds):
        super().__init__(**kwds)

    def setup(self):
        #self.question.settings().setAttribute(\
        #    QtWebEngineWidgets.QWebEngineSettings.PluginsEnabled, True)
        #self.answer.settings().setAttribute(\
        #    QtWebEngineWidgets.QWebEngineSettings.PluginsEnabled, True)
        # Add some dummy QWebEngineEngineViews that will be used to determine the actual
        # size of the rendered html. This information will then be used to
        # determine the optimal split between the question and the answer
        # pane.
        self.question_preview = QtWebEngineWidgets.QWebEngineView()
        self.question_preview.loadFinished.connect(\
            self.question_preview_load_finished)
        self.answer_preview = QtWebEngineWidgets.QWebEngineView()
        self.answer_preview.loadFinished.connect(\
            self.answer_preview_load_finished)
        # Calculate an offset to use in the stretching factor of the boxes,
        # e.g. question_box = question_label + question.
        self.stretch_offset = self.question_label.size().height()
        if self.question_box.spacing() != -1:
            self.stretch_offset += self.question_box.spacing()
        self.scrollbar_width = QtWidgets.QScrollBar().sizeHint().width()
        self.question_text = ""
        self.answer_text = ""
        self.required_question_size = self.question.size()
        self.required_answer_size = self.answer.size()
        self.is_answer_showing = False
        self.times_resized = 0

    #
    # Code to determine optimal QA split based on prerendering the html
    # in a headless server. Does not work yet in PyQt6, because WebEngine
    # does not yet support headless mode.
    # See: https://bugreports.qt.io/browse/QTBUG-50523
    #

    def resizeEvent_off(self, event):
        # Update stretch factors when changing the size of the window.
        self.set_question(self.question_text)
        self.set_answer(self.answer_text)
        # To get this working the first time we start the program (in general,
        # the first one or two resize events, depending on whether or not we
        # changed the window size), we need to explicitly show the contents.
        # (Qt bug?). We don't do this on subsequent resizes to prevent flicker
        # and media replays.
        if self.times_resized < 2:
            self.reveal_question()
            if self.is_answer_showing:
                self.reveal_answer()
            self.times_resized += 1
        return QtWidgets.QWidget.resizeEvent(self, event)

    def question_preview_load_finished(self):
        #webView->page()->runJavaScript("document.documentElement.scrollWidth;",[=](QVariant result){
        #int newWidth=result.toInt();
        #webView->resize(newWidth,webView->height());
        #});

        #webView->page()->runJavaScript("document.documentElement.scrollHeight;",[=](QVariant result){
        #int newHeight=result.toInt();
        #webView->resize(webView->width(),newHeight);
        #});

        pass
        #self.required_question_size = \
        #    self.question_preview.page().currentFrame().contentsSize()
        #self.update_stretch_factors()

    def answer_preview_load_finished(self):
        pass
        #self.required_answer_size = \
        #    self.answer_preview.page().currentFrame().contentsSize()
        #self.update_stretch_factors()

    #
    # TMP workaround involving a heuristic to determine the height.
    #

    import re

    re_img = re.compile(r"""img src=\"file:///(.+?)\"(.*?)>""",
        re.DOTALL | re.IGNORECASE)

    def estimate_height(self, html):
        import math
        from mnemosyne.libmnemosyne.utils import expand_path, _abs_path
        from PIL import Image

        max_img_height = 0
        total_img_width = 0
        for match in self.re_img.finditer(html):
            img_file = match.group(1)
            if not _abs_path(img_file): # Linux issue
                img_file = "/" + img_file
            if not os.path.exists(img_file):
                print("Missing path", img_file)
                continue
            with Image.open(img_file) as im:
                width, height = im.size
                if height > max_img_height:
                    max_img_height = height
                total_img_width += width
        number_of_rows = math.ceil(total_img_width / self.question.width())
        return number_of_rows * max_img_height + 24

    def update_stretch_factors(self):
        if self.config()["QA_split"] != "adaptive":
            return
        if 0: # Using prerendered html
            # Correct the required heights of question and answer for the
            # presence of horizontal scrollbars.
            required_question_height = self.required_question_size.height()
            if self.required_question_size.width() > self.question.width():
                required_question_height += self.scrollbar_width
            required_answer_height = self.required_answer_size.height()
            if self.required_answer_size.width() > self.answer.width():
                required_answer_height += self.scrollbar_width
        else: # Tmp workaround using heuristic
            required_question_height = \
                self.estimate_height(self.question_text)
            required_answer_height = \
                self.estimate_height(self.answer_text)
        total_height_available = self.question.height() + self.answer.height()
        # If both question and answer fit in their own boxes, there is no need
        # to deviate from a 50/50 split.
        if required_question_height < total_height_available / 2 and \
            required_answer_height < total_height_available / 2:
            question_stretch = 50
            answer_stretch = 50
        # Don't be clairvoyant about the answer size, unless we will need
        # a non 50/50 split to start with.
        # If we are only showing the question, we try to limit 'surprising',
        # 'clairvoyant' stretches if they are not needed.
        elif not self.is_answer_showing:
            if required_question_height < total_height_available / 2:
                # No need to be clairvoyant.
                question_stretch = 50
                answer_stretch = 50
            else:
                # Make enough room for the question.
                question_stretch = required_question_height
                if required_question_height + required_answer_height \
                    <= total_height_available:
                    # Already have the stretch set-up to accomodate the answer,
                    # which makes the UI more relaxed (no need to have a
                    # different non 50/50 split once the answer is shown).
                    answer_stretch = required_answer_height
                else:
                    # But if we don't have enough space to show both the
                    # question and the answer, make sure the question gets
                    # all the space it can get now.
                    answer_stretch = 50
        # We are showing both question and answer.
        else:
            answer_stretch = required_answer_height
            if required_question_height + required_answer_height \
                    <= total_height_available:
                # If we have enough space, stretch in proportion to height.
                question_stretch = required_question_height
            else:
                # If we are previewing cards, go for a 50/50 split.
                if not self.used_for_reviewing:
                    question_stretch = 50
                    answer_stretch = 50
                # If we don't have enough space to show both the question and
                # the answer, try to give the answer all the space it needs.
                else:
                    answer_stretch = required_answer_height
                    question_stretch = total_height_available - answer_stretch
                    if question_stretch < 50:
                        question_stretch = 50
        self.setUpdatesEnabled(False)
        self.vertical_layout.setStretchFactor(\
            self.question_box, question_stretch + self.stretch_offset)
        self.vertical_layout.setStretchFactor(\
            self.answer_box, answer_stretch + self.stretch_offset)
        self.setUpdatesEnabled(True)

        # http://stackoverflow.com/questions/37527714/qt-qml-webview-resizes-really-slowly-when-window-resizing


    def silence_media(self, text):
        # Silence media, but make sure the player widget still shows to get
        # correct information about the geometry.
        text = text.replace("var soundFiles = new Array(",
                            "var soundFiles = new Array('off',")
        text = text.replace("<audio src=\"", "<audio src=\"off")
        text = text.replace("<video src=\"", "<video src=\"off")
        return text

    def set_question(self, text):
        #self.main_widget().show_information(text.replace("<", "&lt;"))
        self.question_text = text
        #self.question_preview.page().setPreferredContentsSize(\
        #    QtCore.QSize(self.question.size().width(), 1))
        #self.question_preview.setHtml(self.silence_media(text))
        #self.question_preview.show()

    def set_answer(self, text):
        #self.main_widget().show_information(text.replace("<", "&lt;"))
        self.answer_text = text

        #self.answer_preview.page().setPreferredContentsSize(\
        #    QtCore.QSize(self.answer.size().width(), 1))
        #self.answer_preview.setHtml(self.silence_media(text))
        #self.answer_preview.show()

    def reveal_question(self):
        self.question.setHtml(self.question_text, QtCore.QUrl("file://"))

    def reveal_answer(self):
        self.is_answer_showing = True
        self.update_stretch_factors()
        self.answer.setHtml(self.answer_text, QtCore.QUrl("file://"))
        # Forced repaint seems to make things snappier.
        self.question.repaint()
        self.answer.repaint()

    def clear_question(self):
        self.question.setHtml(self.empty())

    def clear_answer(self):
        self.is_answer_showing = False
        self.update_stretch_factors()
        self.answer.setHtml(self.empty())
        # Forced repaint seems to make things snappier.
        self.question.repaint()
        self.answer.repaint()


class ReviewWdgt(QtWidgets.QWidget, QAOptimalSplit, ReviewWidget, Ui_ReviewWdgt):

    auto_focus_grades = True
    number_keys_show_answer = True

    key_to_grade_map = {QtCore.Qt.Key.Key_QuoteLeft: 0, QtCore.Qt.Key.Key_0: 0,
            QtCore.Qt.Key.Key_1: 1, QtCore.Qt.Key.Key_2: 2, QtCore.Qt.Key.Key_3: 3,
            QtCore.Qt.Key.Key_4: 4, QtCore.Qt.Key.Key_5: 5}

    def __init__(self, **kwds):
        super().__init__(**kwds)
        parent = self.main_widget()

        parent.setCentralWidget(self)
        self.setupUi(self)
        QAOptimalSplit.setup(self)

        # TODO: Move this to designer, once QButtonGroup elements can be set
        # to custom ID from designer.
        self.grade_buttons = QtWidgets.QButtonGroup()
        self.grade_buttons.addButton(self.grade_0_button, 0)
        self.grade_buttons.addButton(self.grade_1_button, 1)
        self.grade_buttons.addButton(self.grade_2_button, 2)
        self.grade_buttons.addButton(self.grade_3_button, 3)
        self.grade_buttons.addButton(self.grade_4_button, 4)
        self.grade_buttons.addButton(self.grade_5_button, 5)
        self.grade_buttons.idClicked[int].connect(self.grade_answer)
        # TODO: remove this once Qt bug is fixed.
        self.setTabOrder(self.grade_1_button, self.grade_2_button)
        self.setTabOrder(self.grade_2_button, self.grade_3_button)
        self.setTabOrder(self.grade_3_button, self.grade_4_button)
        self.setTabOrder(self.grade_4_button, self.grade_5_button)
        self.setTabOrder(self.grade_5_button, self.grade_0_button)
        self.setTabOrder(self.grade_0_button, self.grade_1_button)
        self.focus_widget = None
        self.sched = QtWidgets.QLabel("", parent.status_bar)
        self.notmem = QtWidgets.QLabel("", parent.status_bar)
        self.act = QtWidgets.QLabel("", parent.status_bar)
        self.font = QtGui.QFont()
        self.font.setPointSize(10)
        self.sched.setFont(self.font)
        self.notmem.setFont(self.font)
        self.act.setFont(self.font)
        parent.clear_status_bar()
        parent.add_to_status_bar(self.sched)
        parent.add_to_status_bar(self.notmem)
        parent.add_to_status_bar(self.act)
        parent.status_bar.setSizeGripEnabled(0)
        self.widget_with_last_selection = self.question
        self.question.selectionChanged.connect(self.selection_changed_in_q)
        self.answer.selectionChanged.connect(self.selection_changed_in_a)
        self.media_queue = []
        self.player = None
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)

        # When clicking out of the app, and clicking back on the web widgets,
        # the focus does not get properly restored, and for QWebEngineView, the
        # event handling for keypresses and focusIn events doesn't work, so
        # we do a crude workaround: https://bugreports.qt.io/browse/QTBUG-46251
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.restore_focus)
        self.timer.start(200)

    def deactivate(self):
        self.stop_media()
        ReviewWidget.deactivate(self)

    #def focusInEvent(self, event):
    #    self.restore_focus()
    #    super().focusInEvent(event)

    def changeEvent(self, event):
        if hasattr(self, "show_button"):
            show_button_text = self.show_button.text()
        if event.type() == QtCore.QEvent.Type.LanguageChange:
            self.retranslateUi(self)
        # retranslateUI resets the show button text to 'Show answer',
        # so we need to work around this.
        if hasattr(self, "show_button"):
            self.show_button.setText(_(show_button_text))
        QtWidgets.QWidget.changeEvent(self, event)

    def keyPressEvent(self, event):
        if event.key() in self.key_to_grade_map and not event.isAutoRepeat():
            # Use controller function rather than self.is_answer_showing to
            # deal with the map card type.
            if self.review_controller().is_question_showing():
                if self.number_keys_show_answer:
                    self.show_answer()
            else:
                self.grade_answer(self.key_to_grade_map[event.key()])
        elif event.key() == QtCore.Qt.Key.Key_PageDown:
            self.scroll_down()
        elif event.key() == QtCore.Qt.Key.Key_PageUp:
            self.scroll_up()
        elif event.key() == QtCore.Qt.Key.Key_R and \
            event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:
            self.review_controller().update_dialog(redraw_all=True) #Replay media.
        # QtWebengine issue.
        #elif event.key() == QtCore.Qt.Key.Key_C and \
        #    event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:
        #    self.copy()
        # Work around Qt issue.
        elif event.key() in [QtCore.Qt.Key.Key_Backspace, QtCore.Qt.Key.Key_Delete]:
            self.controller().delete_current_card()
        else:
            QtWidgets.QWidget.keyPressEvent(self, event)

    def empty(self):
        background = self.palette().color(QtGui.QPalette.ColorRole.Base).name()
        if self.review_controller().card:
            colour = self.config().card_type_property(\
            "background_colour", self.review_controller().card.card_type)
            if colour:
                background = ("%X" % colour)[2:] # Strip alpha.
        return """
        <html><head>
        <style type="text/css">
        table { height: 100%; }
        body  { background-color: """ + background + """;
                margin: 0;
                padding: 0;
                border: thin solid #8F8F8F; }
        </style></head>
        <body><table><tr><td>
        </td></tr></table></body></html>"""

    def scroll_down(self):
        return
        # TODO: reimplement after webkit is back.

        if self.review_controller().is_question_showing() or \
           self.review_controller().card.fact_view.a_on_top_of_q:
            frame = self.question.page().mainFrame()
        else:
            frame = self.answer.page().mainFrame()
        x, y = frame.scrollPosition().x(), frame.scrollPosition().y()
        y += int(0.9*(frame.geometry().height()))
        #frame.scroll(x, y) # Seems buggy 20111121.
        frame.evaluateJavaScript("window.scrollTo(%d, %d);" % (x, y))

    def scroll_up(self):
        return
        # TODO: reimplement after webkit is back.

        if self.review_controller().is_question_showing() or \
           self.review_controller().card.fact_view.a_on_top_of_q:
            frame = self.question.page().mainFrame()
        else:
            frame = self.answer.page().mainFrame()
        x, y = frame.scrollPosition().x(), frame.scrollPosition().y()
        y -= int(0.9*(frame.geometry().height()))
        #frame.scroll(x, y)  # Seems buggy 20111121.
        frame.evaluateJavaScript("window.scrollTo(%d, %d);" % (x, y))

    def selection_changed_in_q(self):
        self.widget_with_last_selection = self.question

    def selection_changed_in_a(self):
        self.widget_with_last_selection = self.answer

    #def copy(self):
    #    self.widget_with_last_selection.pageAction(\
    #        QtWebEngineKit.QWebEnginePage.Copy).trigger()

    def show_answer(self):
        self.review_controller().show_answer()

    def grade_answer(self, grade):
        self.review_controller().grade_answer(grade)

    def set_question_box_visible(self, is_visible):
        if is_visible:
            self.question.show()
            self.question_label.show()
        else:
            self.question.hide()
            self.question_label.hide()

    def set_answer_box_visible(self, is_visible):
        if is_visible:
            self.answer.show()
            self.answer_label.show()
        else:
            self.answer.hide()
            self.answer_label.hide()

    def set_question_label(self, text):
        self.question_label.setText(text)

    def restore_focus(self):
        # After clicking on the question or the answer, that widget grabs the
        # focus, so that the keyboard shortcuts no longer work. This functions
        # is used to set the focus back to the correct widget.
        if self.question.hasFocus() or self.answer.hasFocus():
            if self.focus_widget:
                self.focus_widget.setDefault(True)
                self.focus_widget.setFocus()

    def update_show_button(self, text, is_default, is_enabled):
        self.show_button.setText(text)
        self.show_button.setEnabled(is_enabled)
        if is_default:
            self.show_button.setDefault(True)
            self.show_button.setFocus()
            self.focus_widget = self.show_button

    def set_grades_enabled(self, is_enabled):
        self.grades.setEnabled(is_enabled)

    def set_grade_enabled(self, grade, is_enabled):
        self.grade_buttons.button(grade).setEnabled(is_enabled)

    def set_default_grade(self, grade):
        if self.auto_focus_grades:
            # On Windows, we seem to need to clear the previous default
            # first.
            for grade_i in range(6):
                self.grade_buttons.button(grade_i).setDefault(False)
            self.grade_buttons.button(grade).setDefault(True)
            self.grade_buttons.button(grade).setFocus()
            self.focus_widget = self.grade_buttons.button(grade)

    def set_grades_title(self, text):
        self.grades.setTitle(text)

    def set_grade_text(self, grade, text):
        self.grade_buttons.button(grade).setText(text)

    def set_grade_tooltip(self, grade, text):
        self.grade_buttons.button(grade).setToolTip(text)

    def update_status_bar_counters(self):
        scheduled_count, non_memorised_count, active_count = \
            self.review_controller().counters()
        self.sched.setText(_("Scheduled: %d ") % scheduled_count)
        self.notmem.setText(_("Not memorised: %d ") % non_memorised_count)
        self.act.setText(_("Active: %d ") % active_count)

    def redraw_now(self):
        self.repaint()
        self.parent().repaint()

    def play_media(self, filename, start=None, stop=None):
        if self.player == None:
            #print("Initialising mediaplayer")
            #print("Available devices:")
            from PyQt6.QtMultimedia import QMediaDevices
            for device in QMediaDevices().audioOutputs():
                print("  ", device.description())
            self.player = QMediaPlayer()
            self.audio_output = QAudioOutput()
            #print("Selected audio output:", self.audio_output.device().description())
            #print("Volume:", self.audio_output.volume())
            #print("Muted:", self.audio_output.isMuted())
            self.player.setAudioOutput(self.audio_output)
            self.player.mediaStatusChanged.connect(self.player_status_changed)
        if start is None:
            start = 0
        if stop is None:
            stop = 999999
        self.media_queue.append((filename, start, stop))
        if not self.player.playbackState() == \
            QMediaPlayer.PlaybackState.PlayingState:
            self.play_next_file()

    def play_next_file(self):
        filename, self.current_media_start, self.current_media_stop = \
            self.media_queue.pop(0)
        #print("Starting to play", filename)
        self.player.setSource(QtCore.QUrl.fromLocalFile(filename))
        self.player.positionChanged.connect(self.stop_playing_if_end_reached)
        self.player.play()

    def stop_playing_if_end_reached(self, current_position):
        if current_position >= 1000*self.current_media_stop:
            self.player.stop()
            self.play_next_file()

    def player_status_changed(self, result):
        if result == QMediaPlayer.MediaStatus.BufferedMedia:
            self.player.setPosition(int(self.current_media_start*1000))
        elif result == QMediaPlayer.MediaStatus.EndOfMedia:
            #print("End of media reached.")
            if len(self.media_queue) >= 1:
                self.player.positionChanged.disconnect()
                self.play_next_file()
            else:
                self.player.setSource(QtCore.QUrl(None))

    def stop_media(self):
        if self.player:
            self.player.stop()
            self.player.setSource(QtCore.QUrl(None))
        self.media_queue = []
