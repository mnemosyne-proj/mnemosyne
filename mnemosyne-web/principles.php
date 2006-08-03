<?php   include 'include/header.php';
        $lastmod = date ("M d, Y @ h:ia", getlastmod());
?>

<div id="content">

<h1>Principles</h1>
<br>
Here, we discuss some of the principles behind the Mnemosyne project:
<ul>
<li>Spaced repetition</li>
<li>How you use the software</li>
<li>What the nature of the memory research is we envisage</li>
</ul>
<h2>Spaced repetition</h2>
<br>
When you have memorised something, you need to review that material, otherwise you will forget it. However, as you probably know from experience, it is much more effective to space out these revisions over the course over several days, rather than cramming all the revisions in a single session. This is what is called the <i>spacing effect</i>. 
<br><br>
During the past 120 years, there has been considerable research into these aspects of human memory (by e.g. Ebbinghaus, Mace, Leitner and Wozniak). Based on the work of these people, it was shown that in order to get the best results, the intervals between revisions of the same item should gradually increase. This allows you to focus on things you still haven't mastered, while not wasting time on items you remember very well.
<br><br>
It is clear that a computer program can be very valuable in assisting you in this process, by keeping track of how difficult you find an item and by doing the scheduling of the revisions. Let's see how this works in practice in the Mnemosyne program. 
<h2>Using Mnemosyne</h2>
<br>
The software will present you with a question, and your task is trying to remember the answer. Afterwards, you rate yourself on a scale between 0 and 5. These ratings will be used in computing the optimal revision schedule. Let's see what these grades mean.
<br><br>
Grades 0 and 1 are used if you don't know the answer yet, or if you have forgotten it. An item with grade 1 is starting to get more familiar than one with grade 0, and will be repeated less often.
<br><br>
The software will keep on asking you these questions until you give them a grade 2 or higher (the exact grade doesn't matter). Grade 2 basically means that you think you'll be able to remember the item for at least one or two days. It signals the transition between short and long term memory.
<br><br>
So now you've memorised this new item. Mnemosyne will next try to make sure that you do not forget it anymore. It will schedule the next revision of this item to some future date, when it thinks you'll still be able to remember it with some effort, without having forgotten it completely. This is the most efficient for the learning process.
<br><br>
If in the future Mnemosyne asks you the question too soon, and you're able to remember it without any effort, you rate the item a 5. The program will take this into account by waiting a lot longer before asking you this question again.
<br><br>
If Mnemosyne gets it just right, so that you remember it, albeit with some effort, you use grade 4.
<br><br>
If on the other hand it takes you significant effort to remember the answer, and you think the software has waited too long to ask you this question, then rate the item 3.
<br><br>
If you fail to remember it altogether, rate it between 0 and 2 (the exact grade doesn't matter), and Mnemosyne will keep on asking you this question until you think you'll be able to remember it again for a few days.
<br><br>
For best results, it is suggested to do your revisions every day, although Mnemosyne will try to cope as well as possible if you postpone your revisions or if you want to learn ahead of time.
<br>
<h2>Memory research</h2>
<br>
The first thing we will investigate is how well our scheduling algorithm performs (i.e. how often users give the revision a grade 4), how robust it is with respect to late revisions, etc ... .
<br><br>
There are several similar programs out there, implementing different spaced repetition algorithms with various levels of sophistication. However, most of these programs are commercial, and therefore there is no real independently verifiable data that e.g. algorithm A outperforms algorithm B. In order to get such data in a statistically relevant way, one needs two things:
<ul>
<li>A large number of participants.</li>
<li>A study which has no commercial bias.</li> 
</ul>

These two needs are best served with open source software. As Mnemosyne is completely free and will always remain so in the future, there is no barrier for new users to participate. Also, thanks to the internet, we can easily gather the anonymous data, without requiring any user intervention (after they gave their initial permission, of course). Secondly, since we have no commercial interest, there is no need for us to claim that the algorithm in a next (expensive!) version is really better than the one in the version you already bought.
<br><br>
Looking further into the future, we would like to collect this data over a very long time span (years and hopefully decades). This could potentially give us very valuable insight into the nature of long-term memory and the ultimate performace of spaced repetition.

<?php
        include 'include/footer.php';
?>
