<?php   include 'include/header.php';
        $lastmod = date ("M d, Y @ h:ia", getlastmod());
?>

<div id="content">

          There is no comprehensive manual for Mnemosyne (yet), but you can get all the relevant information by reading the <a href="principles.php">principles<a> page and the FAQ below.

<h1>Frequently asked questions</h1>

<h2 id="question">What is the recommended way to organise my items in different categories and files?</h2>
To make your life as easy as possible, we recommend keeping all your items in a single file and use categories to add some structure to them. E.g., to a question 'house' in a category 'Spanish', you'll need to answer 'casa', whereas the same question in the 'French' category requires 'maison'. We recommend that you keep all your categories active at the same time, and let Mnemosyne figure out what items to review. Manually activating and deactivating categories can become very tedious. Keeping each category in a different file requires even more mouse clicks from your part.

<h2 id="question">I've just added a whole lot of new items. What is the best way to starting working with these?</h2>
By default, Mnemosyne will only show you 5 different items you've put in grade 0 at once. This is because it does not make sense to try and memorise e.g. 100 new items all at once. However, you can change this number 5 by using the 'number of grade 0 items to learn at once' option in the 'Configure' menu. If you already know all your items, you can just go through all of them in a single pass and grade them 3, 4 or 5. However, we recommend only going through a limited number of new items each day, in order to help Mnemosyne achieve a better spread of your workload when revising these items again.
   
<h2 id="question">I have a bunch of items in a word processor or a spread sheet program. Can I import them into Mnemosyne?</h2>
Mnemosyne can import plain text files where each line contains a question/answer pair separated by a tab. So e.g. if you have such a list in Word, save it as plain text (*.txt), choose 'other encoding - Unicode (UTF-8)' if your data contains funny characters, and then you get a file which you can import in Mnemosyne if you choose the 'Text with tab separated Q/A' format. The same goes for Excel using 'save as', 'tab delimited (txt)'. However, Excel's unicode text format is not the standard UTF-8, so this only works for latin characters.

<h2 id="question">What other file formats can I import?</h2>
You can import Memaid's XML format (Mnemosyne's predecessor) and also Supermemo7's text format.

<h2 id="question">I'd like to print out a list of my items.</h2>
In the export function, export to a file with extension <code>'.txt'</code>, which you can then open in your favourite word processor.

<h2 id="question">Can I add pictures to questions or anwers?</h2>
Sure, you can use ordinary html-syntax for that:

<code>
&lt;img src="mona-lisa.jpg">
</code>.

The path is relative to the location of your <code>*.mem</code> file, although you can use absolute paths too. You can also use HTML tags to change the colour, formatting and style of your text.

<h2 id="question">How do I best handle mathematical our chemical formulas?</h2>
A low-tech option is to approximate them using ordinary text. For multi-line formulas, it's best to use a fixed-width font, and to mark the checkbox 'left align Q/A' in the preference window. A high-tech option is letting LaTeX render your formulas, e.g.<code>&lt;latex>x^2+y^2=z^2&lt;/latex></code>. For this you need latex and dvipng installed. Windows users can download <a href="http://www.miktex.org/">MiKTeX</a> for that.

<h2 id="question">Adding sounds to question or answers would be nice!</h2>
It sure would! A future version will use html <code>&lt;sound> </code> tags to specify a sound file, which will then be played by an external program (which you can choose).

<h2 id="question">Can I use keyboard shortcuts while doing the revisions?</h2>
Sure! To show the answer you can either press enter, space or return. To grade your answer you can just press the number keys. You can use the delete button to get rid of an item.

<h2 id="question">How can I sort the items in the 'Edit items' list by category?</h2>
Just click on the 'Category' column title. Clicking again changes the sort order.

<h2 id="question">Can I use hierachical categories?</h2>
Not yet, but in the mean time, you can give your categories names like 'Science:Physics' and 'Science:Mathematics'. 

<h2 id="question">What is the best way to backup my data?</h2>
It is recommended that you export all your data to a new XML file from time to time.

<h2 id="question">Exactly what algorithm is used to schedule revisions?</h2>
The algorithm used is very similar to <a href="http://www.supermemo.com/english/ol/sm2.htm">SM2</a> used in one of the early versions of <a href="http://www.supermemo.com">SuperMemo</a>. There are some modifications to be able to deal with early and late repetitions, and to add a small healthy dose of randomness to the intervals.

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
