//
// mnemosyne.c <Peter.Bienstman@UGent.be>
//

#include <stdio.h>

int main(int argc, char *argv[])
{
  // Initialise Python bridge.
  start_python_bridge();

  // Run a few Python commands to initialise Mnemosyne.
  run_python(
    "import sys\n"
    "sys.path.insert(0, \"/home/pbienst/source/mnemosyne-proj-pbienst/mnemosyne\")\n"
    "sys.path.insert(0, \"/home/pbienst/source/mnemosyne-proj-pbienst/mnemosyne-proj/mnemosyne\")\n"
    "from mnemosyne.libmnemosyne import Mnemosyne\n"
    "mnemosyne = Mnemosyne()\n"
    "mnemosyne.components.insert(0, (\"mnemosyne.libmnemosyne.translator\", \"GetTextTranslator\"))\n"
    "mnemosyne.components.append((\"mnemosyne.embedded_in_C.main_wdgt\", \"MainWdgt\"))\n"
    "mnemosyne.components.append((\"mnemosyne.embedded_in_C.review_wdgt\", \"ReviewWdgt\"))\n"
    "mnemosyne.initialise(data_dir=\"/home/pbienst/source/mnemosyne-proj-pbienst/mnemosyne/dot_mnemosyne2\", filename=\"default.db\")\n"
    "mnemosyne.config()[\"upload_science_logs\"] = False\n"
    "mnemosyne.start_review()\n"
    "mnemosyne.review_controller().show_answer()\n"
    "mnemosyne.review_controller().grade_answer(0)\n"
);

  // Illustration on how to get data from Python to C.
  char result[256];
  eval_python_as_unicode("mnemosyne.database().card_count()\n", result, sizeof(result));
  printf("card count: %s\n", result);
  
  // Termination.  
  run_python("mnemosyne.finalise()");
  stop_python_bridge();
}


// For syncing, the python code looks something like this:

//    from openSM2sync.client import Client
//    import mnemosyne.version
//    client = Client(self.machine_id, self.database, self)
//    client.program_name = "Mnemosyne"
//    client.program_version = mnemosyne.version.version
//    client.capabilities = "mnemosyne_dynamic_cards"
//    client.check_for_updated_media_files = False
//    client.interested_in_old_reps = False
//    client.do_backup = True
//    client.upload_science_logs = False
//    try:
//        client.sync(self.server, self.port, self.username, self.password)
//    finally:
//        client.database.release_connection()
