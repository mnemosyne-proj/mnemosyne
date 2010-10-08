
//
// main_widget.c <Peter.Bienstman@UGent.be>
//

#include <stdio.h>

int main_widget_show_question(char* question, char* option_0, char* option_1,
                              char* option_2)
{
  printf("show_question: %s, %s, %s, %s\n", question, option_0, option_1,
         option_2);
  // We should ask the user which option he chooses, but here, we just 
  // hardcode option 0.
  return 0;
}
