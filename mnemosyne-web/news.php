<?php   include 'include/header.php';
        $lastmod = date ("M d, Y @ h:ia", getlastmod());
?>

<div id="content">

<h1>News</h1>


<br>
<b>2007-04-23</b>: released Mnemosyne 0.9.8.1<br>
<br>
(Note that for Windows users we recommend uninstalling the previous
version before doing an upgrade.)<br><br>
-fix scheduling bug when importing new grade 0 items (reported by Jim
Slattery).<br>
-remove incorrect statement with respect to grade 2 behaviour from the
manual. In 0.9.8, the code was changed to be consistent with the old
manual. This has been reverted, so that grade 2 behaviour is again more
like 0.9.7.<br>
<br>
<b>2007-04-13</b>: released Mnemosyne 0.9.8<br>
<br>
-added sound support through tags like <sound src="a.wav">. The path to
 the sound file is either absolute or relative to the location of your
 .mem file. To play the sound again, press the 'R' key in the main window.
 Supported file formats are wav, ogg and mp3. On Linux, this requires
 properly installing pygame and its dependencies like SDL.<br>
-add option to increase size of non-latin characters relative to latin
 characters (together with N. Kriha).<br>
-disable 'edit item' as long as the answer is not shown, to prevent
 accidentally revealing it (patch by D. Herrmann).<br>
-fix handling of < inside latex tags (reported by jgurling, patch by N.
 Kriha).<br>
-warn when exiting an 'Add items' which contains an item which has not
 been added (requested by Airconditioning).<br>
-fix UTF-8 handling in the Supermemo7 file format (reported by Loco)
-fix corner cases in scheduling algorithm (patch by Querido).<br>
-make button ordering more consistent in add items (reported by N. Kriha).<br>
-fixed handling of multiple latex tags (reported by M. Boespflug).<br>
-don't hang on latex errors (reported by M. Boespflug).
-make tab-separated import resistant to the presence of multiple tabs
 (reported by J. Forrez).<br>
-fixed hang when end quotes are not present inside a tag.<br>
-fixed regression where the active flag of categories was not respected on
 import (reported by A. Rachmatullah).<br>
-respect left align option in 'preview items' (reported by E. Grannan).<br>
-making saving more robust while Windows is shutting down (fix by Tom).<br>
-various small interface cleanups and fixes.<br>

<br>
<b>2006-10-27</b>: released Mnemosyne 0.9.7<br>
-multiple items can now be selected in the 'edit items' dialog in order
 to delete them, change their categories, or add their vice versas.<br>
-added option to import text files where question and answer are each on
 their own line.<br>
-again respect window size set by user.<br>
-make delete button work in 'edit items' dialog (reported by J. Forrez).<br>
-worked around oddity (extra first character in text file) when importing
 Word unicode text files.<br>
-various small interface cleanups and fixes.<br>
-updated documentation on the website.<br>

<br>
<b>2006-10-07</b>: released Mnemosyne 0.9.6<br>
-added LaTeX support for formulas, e.g. <code>&lt;latex>x^2+y^2=z^2&lt;/latex></code>. For
 this you need latex and dvipng installed. Windows users can download
 MiKTeX. (thanks to input from Henrik Skov Midtiby and J. David Lee)<br>
-added possibility to preview an item. Useful if you work with tags.<br>
-added import from SuperMemo7 text files (code thanks to Dirk Herrmann).<br>
-either space, enter or return can be used to show the answer. The default
 answer grade is set to 4, which once again can be chosen by either space,
 enter or return (patch by Dirk Herrmann).<br>
-importing of txt files in utf8 unicode encoding now works (patch by Ian
 MacLean).<br>
-exporting to txt files now uses utf8 encoding.<br>
-the total number of items in the status bar now only takes into account
 items in active categories (patch by Mike Charlton).<br>
-prevent infinite recursion when searching for an item that was recently
 deleted.<br>
-the titlebar now displays unicode filenames correctly.<br>
-After the window expands to accomodate a large item, it will shrink
 back again.<br>
-fixed incorrect button text when switching databases.<br>
-new grade 0/1 items will now be scheduled after existing grade 0/1 items.<br>

<br>
<b>2006-08-03</b>: released Mnemosyne 0.9.5<br>
*** IMPORTANT UPGRADE NOTICE ***
<br>
This version uses a different database format. Before upgrading, export your
old data as xml. After upgrade, create a new database and import the old data
from the xml file.<br>
<br>
-databases can now be moved back and forth between Windows and Unix.<br>
-added 'Reset learning data on export' option. This makes it easier to
 create a file to share with other people.<br>
-the database is now saved each time a new item is added.<br>
-fixed a bug where exporting to txt always exported all categories
 (reported by Dariusz Laska).<br>
-items which you forget will no longer be pushed out of the revision queue
 by items which you still need to learn.<br>
<br>
<b>2006-06-04</b>: released Mnemosyne 0.9.4<br>
- category names are now sorted alphabetically.<br>
- relative path names now work for multiple img tags in the same string.
  (patch by J. David Lee).<br>
- removed leftover debug code which could cause problems with Unicode
  items.<br>
<br>
<b>2006-05-25</b>: released Mnemosyne 0.9.3<br>
- relative paths can now be used in img tags, i.e. &ltimg src="foo/bar.png">
  instead of &ltimg src="/home/johndoe/.mnemosyne/foo/bar.png/">. Paths are
  relative to the location of the *.mem file.<br>
- added ability to export to a txt file (only the questions and the
  answers are exported).<br>
- added locking mechanism which warns you if you start a second
  instance of the program, which could lead to data loss.<br>
- fixed obscure button labelling bug (patch by J. David Lee).<br>
<br>
<b>2006-03-25</b>: released Mnemosyne 0.9.2<br>
*** IMPORTANT UPGRADE NOTICE ***
<br>
This version uses a different database format. Before upgrading, export your
old data as xml. After upgrade, create a new database and import the old data
from the xml file.<br>
<br>
- only a limited number of grade 0 items is moved to the learning queue
  at a single time. This is 5 by default, but can be set through the
  configuration screen<br>
- added ability to import from tab separated text files (as exported e.g.
  by Excel)<br>
<br>
<b>2006-02-09</b>: released Mnemosyne 0.9.1<br>
- fixed bug where an item would get asked twice after editing<br>
- fixed bug when using the popup menu on an empty spot<br>
<br>
<b>2006-02-08</b>: released Mnemosyne 0.9 <br>
- first public release

<?php
        include 'include/footer.php';
?>
