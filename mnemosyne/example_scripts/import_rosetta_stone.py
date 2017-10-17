#
# import_rosetta_stone.py <Peter.Bienstman>
#

# Script to import audio and pictures from the Rosetta Stone V2 into a Sentence
# card type.

# Adapt it your own need. It uses linux external tools, so it needs to be
# modified to run under Windows.

import os
import shutil

from mnemosyne.script import Mnemosyne

# 'data_dir = None' will use the default sysem location, edit as appropriate.
data_dir = None
mnemosyne = Mnemosyne(data_dir)

# Answer questions coming from libmnemosyne.

def show_question(question, option0, option1, option2):
    # Aswer 'no' when adding duplicate cards.
    if question.startswith("There is already"):
        return 2
    # Answer 'yes' for making tag active.
    if question.startswith("Make tag"):
        return 0
    else:
        raise NotImplementedError

mnemosyne.main_widget().show_question = show_question

# This script will add tags like TRS Arabic::Unit 1::Lesson 1
tag_prefix = "TRS Arabic"

# Card type.
card_type = mnemosyne.card_type_with_id("6::Arabic MSA sentences")

# Directory containing foreign language, with directories like ARA01_01
# and PCT01_01
foreign_directory = "/home/pbienst/tmp/trs_arabic"

# Directory containing native language, to generate translations.
native_directory = "/home/pbienst/tmp/trs_english"

# Subdirectory in the media directory to used.
media_subdir = "trs_ara"
full_media_subdir = os.path.join(mnemosyne.database().media_dir(), media_subdir)
if not os.path.exists(full_media_subdir):
    os.mkdir(full_media_subdir)

# Codec that was used to encode the foreign language.
foreign_codec = "iso-8859-6"
native_codec = "latin-1"

# Extract txt.
def get_txt(directory, codec):
    txt = {}
    for path in sorted(os.listdir(directory)):
        subdir = os.path.join(directory, path)
        if os.path.isdir(subdir) and not path.startswith("PCT"):
            # Determine unit and lesson number.
            unit, lesson = path[3:].split("_")
            unit = int(unit)
            if unit not in txt:
                txt[unit] = {}
            lesson = int(lesson)
            # Determine sentences.
            txt_file = file(os.path.join(subdir,
                [x for x in os.listdir(subdir) if x.endswith(".TXT")][0]))
            entries = str(txt_file.read(), codec, errors="ignore") \
                .replace(chr(336), "\'") \
                .replace(chr(213), "\'") \
                .replace(chr(210), "\"") \
                .replace(chr(211), "\"") \
                .split("@")[1:-1]
            assert len(entries) == 40
            txt[unit][lesson] = entries
    return txt

foreign_txt = get_txt(foreign_directory, foreign_codec)
native_txt = get_txt(native_directory, native_codec)

# Extract images.
def extract_images(directory):
    images = {}
    for path in sorted(os.listdir(directory)):
        subdir = os.path.join(directory, path)
        if os.path.isdir(subdir) and path.startswith("PCT"):
            # Detemine unit and lesson number.
            unit, lesson = path[3:].split("_")
            unit = int(unit)
            if unit not in images:
                images[unit] = {}
            lesson = int(lesson)
            img_dir = os.path.join(subdir,
                [x for x in os.listdir(subdir) if x.startswith("P")][0])
            img_list = []
            for img in sorted(os.listdir(img_dir)):
                full_path = os.path.join(img_dir, img)
                if img.endswith("JPG"):
                    shutil.copyfile(full_path, os.path.join(full_media_subdir, img))
                    img_list.append(media_subdir + "/" + img)
                if img.endswith("PCT"):
                    os.system("convert " + full_path + " " + \
                        os.path.join(full_media_subdir, img).replace("PCT", "JPG"))
                    img_list.append(\
                        media_subdir + "/" + img.replace("PCT", "JPG"))
            images[unit][lesson] = img_list
    return images

images = extract_images(foreign_directory)

# Extract sound.
def extract_sound(directory):
    sound = {}
    for path in sorted(os.listdir(directory)):
        subdir = os.path.join(directory, path)
        if os.path.isdir(subdir) and not path.startswith("PCT"):
            # Determine unit and lesson number.
            unit, lesson = path[3:].split("_")
            unit = int(unit)
            if unit not in sound:
                sound[unit] = {}
            lesson = int(lesson)
            snd_dir = os.path.join(subdir,
                [x for x in os.listdir(subdir) if x.endswith("S")][0])
            snd_list = []
            for snd in sorted(os.listdir(snd_dir)):
                full_path = os.path.join(snd_dir, snd)
                if snd.endswith("SWA"):
                    os.system("mplayer -vo null -vc dummy -af resample=44100 -ao pcm:waveheader " \
                        + full_path + " && lame audiodump.wav " + \
                        os.path.join(full_media_subdir, snd).replace("SWA", "MP3"))
                    # High bitrate version, not really needed.
                    #os.system("mplayer -vo null -vc dummy -af resample=44100 -ao pcm:waveheader " \
                    #    + full_path + " && lame -h --resample 44.1 -b 128 audiodump.wav " + \
                    #    os.path.join(full_media_subdir, snd).replace("SWA", "MP3"))
                    snd_list.append(\
                        media_subdir + "/" + snd.replace("SWA", "MP3"))
            sound[unit][lesson] = snd_list
    return sound

sound = extract_sound(foreign_directory)

for unit in foreign_txt:
    for lesson in foreign_txt[unit]:
        print(("unit", unit, "lesson", lesson))
        for i in range(40):
            print((foreign_txt[unit][lesson][i]))
            print((native_txt[unit][lesson][i].replace(chr(336), "\'")))
            print((images[unit][lesson][i]))
            print((sound[unit][lesson][i]))
            print()
            fact_data = {"f": "["+foreign_txt[unit][lesson][i] + "]",
                "p_1": "<audio src=\"" + sound[unit][lesson][i] + "\">",
                "m_1": native_txt[unit][lesson][i] + \
                    "\n<img src=\"" + images[unit][lesson][i] + "\">"}
            mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=-1, tag_names=[tag_prefix + "::Unit " + str(unit)\
                + "::Lesson " + str(lesson)])
        print()

mnemosyne.finalise()
