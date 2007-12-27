<?php   include 'include/header.php';
        $lastmod = date ("M d, Y @ h:ia", getlastmod());
?>

<div id="content">

          There is no comprehensive manual for Mnemosyne (yet), but you can get all the relevant information by reading the <a href="principles.php">principles<a> page and the FAQ below.

<h1>Frequently asked questions</h1>

<h2 id="question">What is the recommended way to organise my cards in different categories and files?</h2>
To make your life as easy as possible, we recommend keeping all your cards in a single file and use categories to add some structure to them. E.g., to a question 'house' in a category 'Spanish', you'll need to answer 'casa', whereas the same question in the 'French' category requires 'maison'. We recommend that you keep all your categories active at the same time, and let Mnemosyne figure out what cards to review. Manually activating and deactivating categories can become very tedious. Keeping each category in a different file requires even more mouse clicks from your part.

<h2 id="question">I've just added a whole lot of new cards. What is the best way to starting working with these?</h2>
By default, Mnemosyne will only show you 5 different cards you've put in grade 0 at once. This is because it does not make sense to try and memorise e.g. 100 new cards all at once. However, you can change this number 5 by using the 'number of grade 0 cards to learn at once' option in the 'Configure' menu. If you already know all your cards, you can just go through all of them in a single pass and grade them 3, 4 or 5. However, we recommend only going through a limited number of new cards each day, in order to help Mnemosyne achieve a better spread of your workload when revising these cards again.
  
<h2 id="question">What is the difference between grade 0 and grade 1 cards?</h2>
Grade 1 cards are different from grade 0 cards in the sense that they show up less often and are not subject to the 'number of grade 0 cards to learn at once' setting. This setting is there to prevent you from trying to memorise too many new cards at once. It does <b>not</b> tell you how many new cards you need to learn per day. You are the judge of that: you can learn more cards or less cards, depending on how you feel.

<h2 id="question">Help! I've been away for a few days, and now I have a huge backlog of cards. What is the best way to deal with this?</h2>
Don't worry too much! Do as many cards as you feel like to catch up, the rest will be automatically rescheduled to the future.
 
<h2 id="question">I have a bunch of cards in a word processor or a spread sheet program. Can I import them into Mnemosyne?</h2>
Mnemosyne can import plain text files where each line contains a question/answer pair separated by a tab. So e.g. if you have such a list in Word, save it as plain text (*.txt), choose 'other encoding - Unicode (UTF-8)' if your data contains funny characters, and then you get a file which you can import in Mnemosyne if you choose the 'Text with tab separated Q/A' format. The same goes for Excel using 'save as', 'tab delimited (txt)'. However, Excel's unicode text format is not the standard UTF-8, so this only works for latin characters.

<h2 id="question">What other file formats can I import?</h2>
You can import Memaid's XML format (Mnemosyne's predecessor) and also Supermemo7's text format.

<h2 id="question">I'd like to print out a list of my cards.</h2>
In the export function, export to a file with extension <code>'.txt'</code>, which you can then open in your favourite word processor.

<h2 id="question">What is the three-sided cards feature for, and how do I use it?</h2>
Three-sided cards are useful when dealing with vocabulary in foreign scripts 
 easier. Right clicking the text field in 'add cards' gives you to option
 to switch to 3-sided card input, which replaces the question and answer
 fields by 3 fields: written form, pronunciation, translation. After 
 selecting an initial grade, 2 cards will be added:
<p> Q: written form</p>
<p>  A: pronunciation</p>
<p>     translation</p>
</p>
 and
 <p> Q: translation</p>
<p>  A: written form</p>
 <p>    pronunciation</p>
</p>

Future versions will make sure that a change you make in one pair of the set is automatically reflected in the other one.

<h2 id="question">What about import of three-sided cards?</h2>
For each card, put 'written form', 'pronunciation', and 'translation' on a single line, separated by tabs.


<h2 id="question">I'm studying a language which uses a foreign script, like Japanese. The default font size is too small to make out these funny characters, but if I increase the font size in the preference dialog, also the English text becomes very big.</h2>
There is an option 'increase font size of non-latin characters' which allows you to solve exactly this problem.


<h2 id="question">I love Mnemosyne so much I always want to keep it in my pocket! Can I run the program from a USB drive?</h2>
Sure, copy the Mnemosyne directory from <code>C:\Program Files</code> to your
USB drive, and then copy the <code>.mnemosyne</code> directory from inside 
your home directory to inside the Mnemosyne directory
on the USB drive. Alternatively, you can start mnemosyne with the -d option
 to specify where <code>.mnemosyne</code> directory is located, e.g. 
<code>F:\Mnemosyne\mnemosyne.exe -d F:\.mnemosyne</code>.
<br>
To run the Linux version from a USB key, untar the source file
<code>mnemosyne-X.X.tgz</code> (with X.X the version number) to the USB key. 
Copy your <code>.mnemosyne</code> directory to the USB key as well. 
Change to the directory where the USB key is mounted and type
<br><br><code>
 PYTHONPATH=mnemosyne-X.X python mnemosyne-X.X/mnemosyne/pyqt_ui/mnemosyne -d .
</code><br><br>
 (This assumes that the system you are working on has Python installed, as 
 well as all the libraries Mnemosyne requires.)

<h2 id="question">Can I add images to questions or anwers?</h2>
Sure, using the right mouse button or 'Ctrl+I' brings up a file selection dialog that you can use to choose an image file. This generates tags of the form 
<code>
&lt;img src="mona-lisa.jpg"></code>. (The path is relative to the location of your <code>*.mem</code> file, although you can use absolute paths too. For easy sharing of databases, we recommend that you put all your pictures somewhere inside the <code>.mnemosyne</code> directory.) Note that you can also use HTML tags to change the colour, formatting and style of your text.

<h2 id="question">Adding sounds to question or answers would be nice!</h2>
Using the right mouse button or 'Ctrl+S' brings up a file selection dialog that you can use to choose a sound file. This generates tags of the form <code>&lt;sound src="a.wav"></code>. (The path is relative to the location of your <code>*.mem</code> file, although you can use absolute paths too). To play the sound again, press  'Ctrl+R'  in the main window. Supported file formats are wav, ogg and mp3. On Linux, this requires properly installing pygame and its dependencies like SDL.

<h2 id="question">Can I include mathematical or chemical formulas?</h2>
You can let LaTeX render your formulas, which can be achieved by using tags like <code>&lt;$>x^2+y^2=z^2&lt;/$></code>. For this you need LaTeX and dvipng installed. Windows users can download <a href="http://www.miktex.org/">MiKTeX</a> for that. The error output of LaTeX gets saved to the file <code>.mnemosyne/latex/latex_out.txt</code>.

<h2 id="question">I am a LaTeX guru and I want more control over how my formulas are displayed.</h2>
The <code>&lt;$></code>...<code>&lt;/$></code> tags use LaTeX's inline math environment, but there are two more tags:
<ul>
<li>The <code>&lt;$$></code>...<code>&lt;/$$></code> tags for centered equations on a separate line (LaTeX's <code>displaymath</code> environment)</li>
<li>The <code>&lt;latex></code>...<code>&lt;/latex></code> tags for code which is not in any environment, but just embedded between a typical latex pre- and postamble.</li> 
</ul>
By the way, you can edit what goes into the pre- and postamble by delving into your <code>.mnemosyne/latex</code> directory and editing the aptly named <code>preable</code> and <code>postamble</code> files to your heart's content. While you're there, feel free to edit the <code>dvipng</code> file as well.

<h2 id="question">The preference screen looks so spartan!</h2>
Actually, we prefer the term Zen-like ;-). To avoid cluttering the interface, only the most frequently used options are placed there. Still, if you are an advanced user, you can edit the <code>.mnemosyne/config.py</code> file to get a more fine-grained control over Mnemosyne's behaviour. An example of such a file is <a href="config.py">here</a>. Another customisation option is the plugin mechanism: all the Python files you place inside your <code>.mnemosyne/plugins</code> directory will be executed on startup.

<h2 id="question">How do I change the language Mnemosyne uses?</h2>
By default, the language corresponding to your system's locale is chosen. If you want to override this behaviour, edit your <code>.mnemosyne/config.py</code> file and replace the line <code>locale = None</code> to <code>locale = 'en'</code> or <code>locale = 'es'</code> or whatever.

<h2 id="question">I'm under Linux, and it seems Mnemosyne prevents other programs from using sound.</h2>
Add this to your environment:
<code>export SDL_AUDIODRIVER="alsa"</code>

<h2 id="question">I move back and forth between a Windows machine and a Linux machine. What is the easiest way to synchronise the data on these two computers?</h2>

It is recommended that you place all your files in the <code>.mnemosyne</code> folder. That way, you can just copy that folder around. There are tools which make this synchronisation process a bit easier, e.g. <a href="http://www.cis.upenn.edu/~bcpierce/unison/">Unison</a>. If you have your Linux home directory mounted as <code>Z:\</code> under Windows, you can use a Unison <code>prf</code>-file that looks like this:
<code>
<pre>
root = C:\users\pbienst\.mnemosyne
root = Z:\.mnemosyne
log = false
fastcheck = true
</pre>
</code>

<h2 id="question">What is the best way to share my cards with somebody else?</h2>
                                                                         Export the categories you want to share to XML, and choose 'reset learning data on export'. If your deck contains images or sounds, it's best to keep these in a separate folder inside your <code>.mnemosyne</code> directory and use relative path names to refer to them (the default). That way, the people you are distributing your cards to just need to copy this directory to their <code>.mnemosyne</code> directory.

<h2 id="question">Is there some website where I can upload the cards that I want to share?</h2>
For the time being, you can just email your XML file to the authors, and it will be put for download on the Sourgeforge website. However, this becomes unscalable once a large number of people start to do that, so we are looking for volunteers to implement a website with an upload facility.


<h2 id="question">Can I use keyboard shortcuts while doing the revisions?</h2>
Sure! Here is a list of the keyboard shortcuts you can use:

<ul>
<li>Enter, Space, Return: default action (mostly show answer)
<li>number keys 0-5: grades (use Ctrl+number keys when adding cards)

<li>Ctrl+N: New file</li>
<li>Ctrl+O: Open file</li>
<li>Ctrl+S: Save file (in the main window)</li>
<li>Ctrl+A: Add cards</li>
<li>Ctrl+E: Edit current card</li>
<li>Del:    Delete card</li>
<li>Ctrl+D: Edit deck</li>
<li>Ctrl+G: Activate categories</li>
<li>Ctrl+T: Statistics</li>
<li>Ctrl+S: Insert sound (in the edit fields)</li>
<li>Ctrl+I: Insert image</li>
<li>Ctrl+P: Preview card</li>
<li>Ctrl+F: Find</li>
<li>F3    : Find</li>
<li>Ctrl+P: Preview card</li>
<li>Ctrl+R: Replay sound</li>
</ul>
In text fields, the standard cut, copy, paste, undo and redo shortcuts
are available

<h2 id="question">How can I sort the cards in the 'Edit deck' list by category?</h2>
Just click on the 'Category' column title. Clicking again changes the sort order.

<h2 id="question">Can I use hierachical categories?</h2>
Not yet, but in the mean time, you can give your categories names like 'Science:Physics' and 'Science:Mathematics'. 

<h2 id="question">What is the best way to backup my data?</h2>
The best way to backup your data is to copy your <code>.mnemosyne</code> directory (if you follow the recommended procedure to keep all your files there) and move it to a different drive. Mnemosyne keeps automatic XML-based backups in .mnemosyne/backups, but that won't help you if that drive dies...

<h2 id="question">Exactly what algorithm is used to schedule revisions?</h2>
The algorithm used is very similar to <a href="http://www.supermemo.com/english/ol/sm2.htm">SM2</a> used in one of the early versions of <a href="http://www.supermemo.com">SuperMemo</a>. There are some modifications to be able to deal with early and late repetitions, and to add a small healthy dose of randomness to the intervals.

<h2 id="question">But Supermemo now uses SM11. Doesn't this mean that Mnemosyne is a lot worse than Supermemo?</h2>
Perhaps. Perhaps not. We are personally a bit skeptical that the huge complexity of these new algorithms provides for a statistically relevant benefit. But that is one of the facts we hope to find out with our data collection. We will only make modifications to our algorithms either based on common sense, or if the data tells us that there is a statistically relevant reason to do so.

<h2 id="question">Exactly what kind of data is uploaded to the server? Is it really anonymous?</h2>
You are given a random number as identification, which cannot be traced back to you. Also, the questions/answers are only identified as numerical IDs, which hold no information about the text of the cards. So you can safely use Mnemosyne to help you remember to the number of your safe! If you want to see for yourself the data that is uploaded, take a look at the file <code>log.txt
</code> in the <code>.mnemosyne</code> directory in your home directory.

<h2 id="question">Do I need to be online everytime I use the program?</h2>
Not at all. Only when there is enough log data to send to the server (64K uncompressed) will the file be uploaded. If you are offline at that time, Mnemosyne will keep on trying to upload every time you start the program.

<h2 id="question">How long will the Mnemosyne project run?</h2>
We plan to have this project run for as long as possible, years and hopefully decades. If we want to look at long-term memory, that is obviously vital.

<h2 id="question">Will the data collected by the project be available to anyone?</h2>
Sure! The data was contributed by people on a voluntary basis, so it would be unethical to restrict access to it or charge money for it. Anyone interested can contact us to help analyse the data. We only ask that, should that analysis ever result in a scientific journal paper, we become coauthors of that paper.

      <h2 id="question">When I start the program under Windows, I get a message about a missing <code>'~\\.mnemosyne'</code> directory</h2>
In the system control panel, go to 'system settings' and add <code>HOMEPATH=%USERPROFILE%</code> to your environment variables. You might need a reboot. If that fails, you can always try <code>HOMEPATH=C:\</code> or something. 


<?php
        include 'include/footer.php';
?>
