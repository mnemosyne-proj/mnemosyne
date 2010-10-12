//
// review_wdgt.c <Peter.Bienstman@UGent.be>
//
//   Template, to be replaced by functions which actually do something useful
//   in a specific client.
//

#include <stdio.h>

void review_wdgt_set_question_box_visible(int is_visible)
{
  printf("set_question_box_visible: %d\n", is_visible);
}

        
void review_wdgt_set_answer_box_visible(int is_visible)
{
  printf("set_answer_box_visible: %d\n", is_visible);
}        


void review_wdgt_set_question_label(char* text)
{
  printf("set_question_label: %s\n", text);
}
        

void review_wdgt_set_question(char* text)
{
  printf("set_question: %s\n", text);
}        


void review_wdgt_set_answer(char* text)
{
  printf("set_answer: %s\n", text);
}
        

void review_wdgt_clear_question() 
{
  printf("clear_question\n");
}        


void review_wdgt_clear_answer() 
{
  printf("clear_answer\n");
}        


void review_wdgt_update_show_button(char* text, int is_default, int is_enabled) 
{
  printf("update_show_button: %s %d %d\n", text, is_default, is_enabled);
}


void review_wdgt_set_grades_enabled(int is_enabled)
{
  printf("set_grades_enabled: %d\n", is_enabled);
}    


void review_wdgt_set_grade_enabled(int grade, int is_enabled)
{
  printf("set_grade_enabled: %d %d\n", grade, is_enabled);
}    


void review_wdgt_set_default_grade(int grade)
{
  printf("set_default_grade: %d\n", grade);
}        


void review_wdgt_set_grades_title(char* text) 
{
  printf("set_grades_title: %s\n", text);
}            


void review_wdgt_set_grade_text(int grade, char* text) 
{
  printf("set_grade_text: %d %s\n", grade, text);
}            


void review_wdgt_set_grade_tooltip(int grade, char* text) 
{
  printf("set_grade_tooltip: %d %s\n", grade, text);
}


void review_wdgt_update_status_bar(char* message)
// Should also update the counters.
{
  printf("update_status_bar: %s\n", message);
}
