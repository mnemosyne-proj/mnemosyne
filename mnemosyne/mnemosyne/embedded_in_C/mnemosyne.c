
//
// mnemosyne.c <Peter.Bienstman@UGent.be>
//

#include <stdio.h>

int main(int argc, char *argv[])
{
  // Initialisation.
  start_python_bridge();
  

  PyRun_SimpleString(
    "import sys\n"
    "sys.path.insert(0, \"/home/pbienst/source/mnemosyne-proj-pbienst/mnemosyne\")\n"
    "sys.path.insert(0, \"/home/pbienst/source/mnemosyne-proj-pbienst/mnemosyne-proj/mnemosyne\")\n"
    "from mnemosyne.libmnemosyne import Mnemosyne\n"
    "mnemosyne = Mnemosyne()\n"
    "mnemosyne.components.insert(0, (\"mnemosyne.libmnemosyne.translator\", \"GetTextTranslator\"))\n"
    "mnemosyne.components.append((\"mnemosyne.embedded_in_C.C_main_widget\", \"C_MainWidget\"))\n"
    "mnemosyne.components.append((\"mnemosyne.embedded_in_C.C_review_widget\", \"C_ReviewWidget\"))\n"
    "mnemosyne.initialise(data_dir=\"/home/pbienst/source/mnemosyne-proj-pbienst/mnemosyne/dot_mnemosyne2\", filename=\"default.db\")\n"
    "mnemosyne.config()[\"upload_science_logs\"] = False\n"
    "mnemosyne.main_widget().show_question(\"q\", \"0\",\"1\")\n"    
    "mnemosyne.main_widget().get_filename_to_save(\"q\", \"0\",\"1\")\n"
    "mnemosyne.main_widget().enable_edit_current_card(False)\n"
);

  // Illustration on how to get data from Python to C.

  char result[256];
  eval_python_as_unicode("1", result, sizeof(result));
  printf("result as string: %s\n", result);
  
  // Termination.
  stop_python_bridge();
}
