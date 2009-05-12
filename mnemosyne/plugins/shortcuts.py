#
# shortcuts.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component_manager import review_widget

# Don't have Mnemosyne set the focus to grades. This disables space
# enter, and return as shortcut for the grades. Comment this if you
# still want this.

review_widget().auto_focus_grades = False

# Change shortcuts for the grade buttons.

review_widget().grade_0_button.setShortcut("q")
review_widget().grade_1_button.setShortcut("w")
review_widget().grade_2_button.setShortcut("e")
review_widget().grade_3_button.setShortcut("r")
review_widget().grade_4_button.setShortcut("t")
review_widget().grade_5_button.setShortcut("y")

# Some more examples.

#review_widget().grade_0_button.setShortcut("Enter") # Numerical keypad
#review_widget().grade_1_button.setShortcut("Space")
#review_widget().grade_2_button.setShortcut("Return") 
