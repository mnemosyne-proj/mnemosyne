//
// main_wdgt.c <Peter.Bienstman@UGent.be>
//
//   Template, to be replaced by functions which actually do something useful
//   in a specific client.
//

#include <stdio.h>
#include <string.h>

void main_wdgt_set_window_title(char* title)
{
  printf("set_window_title: %s\n", title);
}


void main_wdgt_show_information(char* message)
{
  printf("show_information: %s\n", message);
}


int main_wdgt_show_question(char* question, char* option_0, char* option_1,
                              char* option_2)
{
  printf("show_question: %s, %s, %s, %s\n", question, option_0, option_1,
         option_2);
  // As an example, we hardcode the reply.
  return 0;
}


void main_wdgt_show_error(char* message)
{
  printf("show_error: %s\n", message);
}


void main_wdgt_get_filename_to_open(char* path, char* filter, char *caption,
                                      char* filename, int str_size)
{
  printf("get_filename_to_open: %s, %s, %s\n", path, filter, caption);
  // As an example, we hardcode the reply.
  strncpy(filename, "example_path", str_size);
}


void main_wdgt_get_filename_to_save(char* path, char* filter, char *caption,
                                      char* filename, int str_size)
// Should warn about overwriting existing file.
{
  printf("get_filename_to_save: %s, %s, %s\n", path, filter, caption);
  // As an example, we hardcode the reply.
  strncpy(filename, "example_path", str_size);
}


void main_wdgt_set_status_bar_message(char* message)
{
  printf("set_status_bar_message: %s\n", message);
}


void main_wdgt_set_progress_text(char* text)
{
  printf("set_progress_text: %s\n", text);
}


void main_wdgt_set_progress_range(int min, int max)
{
  printf("set_progress_range: %d %d\n", min, max);
}


void main_wdgt_set_progress_update_interval(int interval)
{
  printf("set_progress_update_interval: %d\n", interval);
}


void main_wdgt_set_progress_value(int value)
{
  printf("set_progress_value: %d\n", value);
}


void main_wdgt_close_progress()
{  
  printf("close_progress\n");
}


void main_wdgt_enable_edit_current_card(int is_enabled)
{
  printf("enable_edit_current_card: %d\n", is_enabled);
}


void main_wdgt_enable_delete_current_card(int is_enabled)
{
  printf("enable_delete_current_card: %d\n", is_enabled);
}


void main_wdgt_enable_browse_cards(int is_enabled)
{
  printf("enable_browse_cards: %d\n", is_enabled);
}
