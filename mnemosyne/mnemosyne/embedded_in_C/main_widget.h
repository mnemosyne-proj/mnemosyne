
//
// main_widget.h <Peter.Bienstman@UGent.be>
//

void main_widget_set_window_title(char* title);

void main_widget_show_information(char* message);

int main_widget_show_question(char* question, char* option_0, char* option_1,
                              char* option_2);

void main_widget_show_error(char* message);

void main_widget_get_filename_to_open(char* path, char* filter, char *caption,
                                      char* filename, int str_size);

void main_widget_get_filename_to_save(char* path, char* filter, char *caption,
                                      char* filename, int str_size);
// Should check for overwritin existing file.


