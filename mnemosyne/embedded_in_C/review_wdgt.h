//
// review_wdgt.h <Peter.Bienstman@gmail.com>
//

void review_wdgt_set_question_box_visible(int is_visible);

        
void review_wdgt_set_answer_box_visible(int is_visible);


void review_wdgt_set_question_label(char* text);
        

void review_wdgt_set_question(char* text);


void review_wdgt_set_answer(char* text);
        

void review_wdgt_clear_question(); 


void review_wdgt_clear_answer(); 


void review_wdgt_update_show_button(char* text, int is_default, int is_enabled); 


void review_wdgt_set_grades_enabled(int is_enabled);


void review_wdgt_set_grade_enabled(int grade, int is_enabled);


void review_wdgt_set_default_grade(int grade);


void review_wdgt_set_grades_title(char* text); 


void review_wdgt_set_grade_text(int grade, char* text); 


void review_wdgt_set_grade_tooltip(int grade, char* text); 


void review_wdgt_update_status_bar_counters();


void review_wdgt_redraw_now();