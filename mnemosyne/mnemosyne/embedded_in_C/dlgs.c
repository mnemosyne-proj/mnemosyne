//
// dlgs.c <Peter.Bienstman@UGent.be>
//
//   Template, to be replaced by functions which actually do something useful
//   in a specific client.
//

#include <stdio.h>
#include <string.h>
#include "python_bridge.h"

void add_cards_dlg_activate()
{
  printf("add_cards_dlg\n");
  run_python(
    "fact_data = {\"q\": \"question\", \"a\": \"answer\"}\n"
    "card_type = self.card_type_by_id(\"1\")\n"
    "mnemosyne.controller().create_new_cards(fact_data, card_type, grade=-1, tag_names=[\"default\"])\n");
}


void edit_card_dlg_activate(char* card_id, int allow_cancel)
{
  printf("edit_card_dlg: %s %d\n", card_id, allow_cancel);
}


void activate_cards_dlg_activate()
{
  printf("activate_cards_dlg\n");
}


void browse_cards_dlg_activate()
{
  printf("browse_cards_dlg\n");
}


void card_appearance_dlg_activate()
{
  printf("card_appearance_dlg\n");
}


void activate_plugins_dlg_activate()
{
  printf("activate_plugins_dlg\n");
}


void manage_card_types_dlg_activate()
{
  printf("manage_card_types_dlg\n");
}
    

void statistics_dlg_activate()
{
  printf("statistics_dlg\n");
}
    

void configuration_dlg_activate()
{
  printf("configuration_dlg\n");
}

    
void sync_dlg_activate()
{
  printf("sync_dlg\n");
  run_python(
    "from openSM2sync.client import Client\n"
    "import mnemosyne.version\n"
    "client = Client(mnemosyne.machine_id, mnemosyne.database, self)\n"
    "client.program_name = \"Mnemosyne\"\n"
    "client.program_version = mnemosyne.version.version\n"
    "client.capabilities = \"mnemosyne_dynamic_cards\"\n"
    "client.check_for_updated_media_files = False\n"
    "client.interested_in_old_reps = False\n"
    "client.do_backup = True\n"
    "client.upload_science_logs = False\n"
    "try:\n"
    "    client.sync(\"server\", 8512, \"username\", \"password\")\n"
    "finally:\n"
    "    client.database.release_connection()\n");
}
