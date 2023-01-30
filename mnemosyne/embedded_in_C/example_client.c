//
// mnemosyne.c <Peter.Bienstman@gmail.com>
//

// Very simple client illustrating the basic structure of a frontend which
// embeds Mnemosyne in C.
// Also consult 'How to write a new frontend' in the docs of libmnemosyne for
// more information about the interaction between libmnemosyne and a frontend.

#include <stdio.h>
#include "python_bridge.h"

int main(int argc, char* argv[])
{
  // Initialise Python bridge.
  start_python_bridge();

  // Run a few Python commands to initialise Mnemosyne.
  run_python(
    "import sys\n"
    "sys.path.insert(0, \"/home/pbienst/source/mnemosyne-proj-pbienst/mnemosyne\")\n"
    "from mnemosyne.libmnemosyne import Mnemosyne\n"
    "mnemosyne = Mnemosyne(upload_science_logs=False, interested_in_old_reps=False)\n"
    "mnemosyne.components.insert(0, (\"mnemosyne.libmnemosyne.translator\", \"GetTextTranslator\"))\n"
    "mnemosyne.components.append((\"mnemosyne.embedded_in_C.main_wdgt\", \"MainWdgt\"))\n"
    "mnemosyne.components.append((\"mnemosyne.embedded_in_C.review_wdgt\", \"ReviewWdgt\"))\n"
    "mnemosyne.components.append((\"mnemosyne.embedded_in_C.dlgs\", \"AddCardsDlg\"))\n"    
    "mnemosyne.components.append((\"mnemosyne.embedded_in_C.dlgs\", \"EditCardDlg\"))\n"    
    "mnemosyne.components.append((\"mnemosyne.embedded_in_C.dlgs\", \"SyncDlg\"))\n"
    "mnemosyne.initialise(data_dir=\"/home/pbienst/source/mnemosyne-proj-pbienst/mnemosyne/dot_mnemosyne2\", filename=\"default.db\")\n"
    "mnemosyne.start_review()\n"
    "mnemosyne.controller().show_add_cards_dialog()\n"
    "mnemosyne.review_controller().show_answer()\n"
    "mnemosyne.review_controller().grade_answer(0)\n"
);

  // For syncing, the python code looks something like this:
  // mnemosyne.controller().sync(server, port, username, password)

  // Illustration on how to get data from Python to C.
  char result[256];
  eval_python_as_unicode("mnemosyne.database().card_count()\n", 
                         result, sizeof(result));
  printf("card count: %s\n", result);
  
  // Termination.  
  run_python("mnemosyne.finalise()");
  stop_python_bridge();
}
