<?php   include 'include/header.php';
        $lastmod = date ("M d, Y @ h:ia", getlastmod());
?>

<div id="content">

<h1>Welcome to the Mnemosyne Project</h1>
<br>
The Mnemosyne Project has two aspects:
<ul>
<li>It's a sophisticated free flash-card tool which optimises your learning process.</li>
<li>It's a research project into the nature of long-term memory.</li>
</ul>
<h2>Efficient learning</h2>
<br>
The Mnemosyne software resembles a traditional flash-card program to help you memorise question/answer pairs, but with an important twist: it uses a sophisticated algorithm to schedule the best time for a card to come up for review.
 Difficult cards that you tend to forget quickly will be scheduled more often, while Mnemosyne won't waste your time on things you remember well.
<br><br>
The software runs on Linux, Windows and <a href="http://snozle.com/2007/05/20/installing-mnemosyne-on-osx-revisited">Mac OSX</a>.
<h2>Memory research</h2>
<br>
While you use the software, detailed statistics can be kept on your learning process. If you want, these logs can be uploaded in a transparent and anonymous way to a central server for analysis. 
<br><br>
This data will be valuable to study the behaviour of our memory over a very long time period. As an additional benefit, the results will be used to improve the scheduling algorithms behind the software even further.

<?php
        include 'include/footer.php';
?>
