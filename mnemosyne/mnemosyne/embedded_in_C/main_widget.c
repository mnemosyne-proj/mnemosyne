
//
// main_widget.c <Peter.Bienstman@UGent.be>
//
//   Template, to be replaced by functions which actually do something useful
//   in a specific client.
//

#include <stdio.h>
#include <string.h>

void main_widget_set_window_title(char* title)
{
  printf("set_window_title: %s\n", title);
}


void main_widget_show_information(char* message)
{
  printf("show_information: %s\n", message);
}


int main_widget_show_question(char* question, char* option_0, char* option_1,
                              char* option_2)
{
  printf("show_question: %s, %s, %s, %s\n", question, option_0, option_1,
         option_2);
  // As an example, we hardcode the reply.
  return 0;
}


void main_widget_show_error(char* message)
{
  printf("show_error: %s\n", message);
}


void main_widget_get_filename_to_open(char* path, char* filter, char *caption,
                                      char* filename, int str_size)
{
  printf("get_filename_to_open: %s, %s, %s\n", path, filter, caption);
  // As an example, we hardcode the reply.
  strncpy(filename, "example_path", str_size);
}


void main_widget_get_filename_to_save(char* path, char* filter, char *caption,
                                      char* filename, int str_size)
// Should check for overwritin existing file.
{
  printf("get_filename_to_save: %s, %s, %s\n", path, filter, caption);
  // As an example, we hardcode the reply.
  strncpy(filename, "example_path", str_size);
}

