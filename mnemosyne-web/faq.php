<?php   include 'include/header.php';
        $lastmod = date ("M d, Y @ h:ia", getlastmod());
?>

<div id="content">

<h1>Frequently asked questions</h1>

<h2 id="question">Can I import data from MemAid?</h2>
If your favorite Memaid client has that option, export your data as XML. You can then import this data into Mnemosyne.

<h2 id="question">What about importing from a text file?</h2>
You can import from a file with extension <code>'.txt'</code> where each line consists of a question and an answer, separated by a tab.

<h2 id="question">I'd like to print out a list of my items.</h2>
In the export function, export to a file with extension <code>'.txt'</code>, which you can then open in your favourite word processor.

<h2 id="question">What's the deal with the 'number of grade 0 items to learn at once' option?</h2>
When you add lots of new items to your database, you obviously won't be able to learn them all at once. By default, Mnemosyne will concentrate on only 5 new items at a time, although you can change this number using this setting.

<h2 id="question">Can I add pictures to questions or anwers?</h2>
Sure, you can use ordinary html-syntax for that:

<code>
&lt;img src="mona-lisa.jpg">
</code>.

The path is relative to the location of your <code>*.mem</code> file, although you can use absolute paths too. You can also use HTML tags to change the colour, formatting and style of your text.

<h2 id="question">How do I handle mathematical our chemical formulas?</h2>
You can either import them as picture, or approximate them using ordinary text. For multi-line formulas, it's best to use a fixed-width font, and to mark the checkbox 'left align Q/A' in the preference window.

<h2 id="question">Adding sounds to question or answers would be nice!</h2>
It sure would! A future version will use html <code>&lt;sound> </code> tags to specify a sound file, which will then be played by an external program (which you can choose).

<h2 id="question">Can I use keyboard shortcuts while doing the revisions?</h2>
Sure! Press enter on the numerical keypad to show the answer, and then use the numerical keypad again to grade your answer.

<h2 id="question">Can I use hierachical categories?</h2>
Not yet, but in the mean time, you can give your categories names like 'Science:Physics' and 'Science:Mathematics'. 

<h2 id="question">What is the best way to backup my data?</h2>
It is recommended that you export all your data to a new XML file from time to time.

<h2 id="question">Exactly what algorithm is used to schedule revisions?</h2>
The algorithm used is very similar to <a href="http://www.supermemo.com/english/ol/sm2.htm">SM2</a> used in one of the early versions of <a href="http://www.supermemo.com">SuperMemo</a>. There are some modifications to be able to deal with early and late repitions, and to add a small healthy dose of randomness to the intervals.

<h2 id="question">But Supermemo now uses SM11. Doesn't this mean that Mnemosyne is a lot worse than Supermemo?</h2>
Perhaps. Perhaps not. We are personally a bit skeptical that the huge complexity of these new algorithms provides for a statistically relevant benefit. But that is one of the facts we hope to find out with our data collection. We will only make modifications to our algorithms either based on common sense, or if the data tells us that there is a statistically relevant reason to do so.

<h2 id="question">Exactly what kind of data is uploaded to the server? Is it really anonymous?</h2>
You are given a random number as identification, which cannot be traced back to you. Also, the questions/answers are only identified as numerical IDs, which hold no information about the text of the items. So you can safely use Mnemosyne to help you remember to the number of your safe! If you want to see for yourself the data that is uploaded, take a look at the file <code>log.txt
</code> in the <code>.mnemosyne</code> directory in your home directory.

<h2 id="question">Do I need to be online everytime I use the program?</h2>
Not at all. Only when there is enough log data to send to the server (64K uncompressed) will the file be uploaded. If you are offline at that time, Mnemosyne will keep on trying to upload every time you start the program.

<h2 id="question">How long will the Mnemosyne project run?</h2>
We plan to have this project run for as long as possible, years and hopefully decades. If we want to look at long-term memory, that is obviously vital.

<h2 id="question">Will the data collected by the project be available to anyone?</h2>
Sure! The data was contributed by people on a voluntary basis, so it would be unethical to restrict access to it or charge money for it. Anyone interested can contact us to help analyse the data.

      <h2 id="question">When I start the program under Windows, I get a message about a missing <code>'~\\.mnemosyne'</code> directory</h2>
In your system settings, add <code>HOMEPATH=%USERPROFILE$</code> to your environment variables.


<?php
        include 'include/footer.php';
?>
