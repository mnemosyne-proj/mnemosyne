<?php   include 'include/header.php';
        $lastmod = date ("M d, Y @ h:ia", getlastmod());
?>

<div id="content">

<h1>News</h1>
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
