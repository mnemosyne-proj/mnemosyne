//
// python_bridge.c <Peter.Bienstman@UGent.be>
//
 
#define STR_SIZE 128

#include <string.h>
#include <stdlib.h>
#include <Python.h>
#include "main_wdgt.h"
#include "review_wdgt.h"
#include "python_stdout_stderr.h"

//
// Functions relating to main widget.
//

static PyObject* _main_wdgt_set_window_title(PyObject* self, PyObject* args)
{
  char* text = NULL;
  if (!PyArg_ParseTuple(args, "s", &text)) 
    return NULL;
  main_wdgt_set_window_title(text);
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _main_wdgt_show_information(PyObject* self, PyObject* args)
{
  char* text = NULL;
  if (!PyArg_ParseTuple(args, "s", &text)) 
    return NULL;
  main_wdgt_show_information(text);
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _main_wdgt_show_question(PyObject* self, PyObject* args)
{
  char* text = NULL;
  char* option_0 = NULL;
  char* option_1 = NULL;
  char* option_2 = NULL;
  if (!PyArg_ParseTuple(args, "ssss", &text, &option_0, &option_1,
        &option_2)) 
    return NULL;
  int answer;
  answer = main_wdgt_show_question(text, option_0, option_1, option_2);
  return Py_BuildValue("i", answer);
}


static PyObject* _main_wdgt_show_error(PyObject* self, PyObject* args)
{
  char* text = NULL;
  if (!PyArg_ParseTuple(args, "s", &text)) 
    return NULL;
  main_wdgt_show_error(text);
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _main_wdgt_get_filename_to_open(PyObject* self, 
                                                 PyObject* args)
{
  char* path = NULL;
  char* filter = NULL;
  char* caption = NULL;
  if (!PyArg_ParseTuple(args, "sss", &path, &filter, &caption))
    return NULL;
  char filename[STR_SIZE+1];
  main_wdgt_get_filename_to_open(path, filter, caption, filename, STR_SIZE);
  return PyUnicode_FromString(filename);
}


static PyObject* _main_wdgt_get_filename_to_save(PyObject* self,
                                                 PyObject* args)
{
  char* path = NULL;
  char* filter = NULL;
  char* caption = NULL;
  if (!PyArg_ParseTuple(args, "sss", &path, &filter, &caption))
    return NULL;
  char filename[STR_SIZE+1];
  main_wdgt_get_filename_to_save(path, filter, caption, filename, STR_SIZE);
  return PyUnicode_FromString(filename);
}


static PyObject* _main_wdgt_set_status_bar_message(PyObject* self, 
                                                   PyObject* args)
{
  char* text = NULL;
  if (!PyArg_ParseTuple(args, "s", &text))
    return NULL;
  main_wdgt_set_status_bar_message(text);
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _main_wdgt_set_progress_text(PyObject* self, PyObject* args)
{
  char* text = NULL;
  if (!PyArg_ParseTuple(args, "s", &text)) 
    return NULL;
  main_wdgt_set_progress_text(text);
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _main_wdgt_set_progress_range(PyObject* self, PyObject* args)
{
  int min = 0;
  int max = 0;
  if (!PyArg_ParseTuple(args, "ii", &min, &max)) 
    return NULL;
  main_wdgt_set_progress_range(min, max);
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _main_wdgt_set_progress_update_interval(PyObject* self,
                                                         PyObject* args)
{
  int interval = 0;
  if (!PyArg_ParseTuple(args, "i", &interval)) 
    return NULL;
  main_wdgt_set_progress_update_interval(interval);
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _main_wdgt_set_progress_value(PyObject* self, PyObject* args)
{
  int value = 0;
  if (!PyArg_ParseTuple(args, "i", &value)) 
    return NULL;
  main_wdgt_set_progress_value(value);
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _main_wdgt_close_progress(PyObject* self, PyObject* args)
{
  main_wdgt_close_progress();
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _main_wdgt_enable_edit_current_card(PyObject* self, 
                                                     PyObject* args)
{
  int is_enabled = 0;
  if (!PyArg_ParseTuple(args, "i", &is_enabled)) 
    return NULL;
  main_wdgt_enable_edit_current_card(is_enabled);
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _main_wdgt_enable_delete_current_card(PyObject* self,
                                                       PyObject* args)
{
  int is_enabled = 0;
  if (!PyArg_ParseTuple(args, "i", &is_enabled)) 
    return NULL;
  main_wdgt_enable_delete_current_card(is_enabled);
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _main_wdgt_enable_browse_cards(PyObject* self,
                                                PyObject* args)
{
  int is_enabled = 0;
  if (!PyArg_ParseTuple(args, "i", &is_enabled)) 
    return NULL;
  main_wdgt_enable_browse_cards(is_enabled);
  Py_INCREF(Py_None);
  return Py_None;
}


static PyMethodDef main_wdgt_methods[] = {
  {"set_window_title",             _main_wdgt_set_window_title, 
   METH_VARARGS, ""},
  {"show_information",             _main_wdgt_show_information, 
   METH_VARARGS, ""},
  {"show_question",                _main_wdgt_show_question, 
   METH_VARARGS, ""},
  {"show_error",                   _main_wdgt_show_error, 
   METH_VARARGS, ""},
  {"get_filename_to_open",         _main_wdgt_get_filename_to_open, 
   METH_VARARGS, ""},
  {"get_filename_to_save",         _main_wdgt_get_filename_to_save, 
   METH_VARARGS, ""},
  {"set_status_bar_message",       _main_wdgt_set_status_bar_message, 
   METH_VARARGS, ""},
  {"set_progress_text",            _main_wdgt_set_progress_text, 
   METH_VARARGS, ""},
  {"set_progress_range",           _main_wdgt_set_progress_range, 
   METH_VARARGS, ""},
  {"set_progress_update_interval", _main_wdgt_set_progress_update_interval, 
   METH_VARARGS, ""},
  {"set_progress_value",           _main_wdgt_set_progress_value, 
   METH_VARARGS, ""},
  {"close_progress",               _main_wdgt_close_progress, 
   METH_VARARGS, ""},
  {"enable_edit_current_card",     _main_wdgt_enable_edit_current_card, 
   METH_VARARGS, ""},
  {"enable_delete_current_card",   _main_wdgt_enable_delete_current_card, 
   METH_VARARGS, ""},
  {"enable_browse_cards",          _main_wdgt_enable_browse_cards, 
   METH_VARARGS, ""},
  {NULL, NULL, 0, NULL}
};


PyMODINIT_FUNC
init__main_wdgt(void)
{
  Py_InitModule("_main_wdgt", main_wdgt_methods);
}



//
// Functions relating to review widget.
//

static PyObject* _review_wdgt_set_question_box_visible(PyObject* self, 
                                                       PyObject* args)
{
  int is_visible = 0;
  if (!PyArg_ParseTuple(args, "i", &is_visible))
    return NULL;
  review_wdgt_set_question_box_visible(is_visible);
  Py_INCREF(Py_None);
  return Py_None;
}
        
static PyObject* _review_wdgt_set_answer_box_visible(PyObject* self, 
                                                     PyObject* args)
{
  int is_visible = 0;
  if (!PyArg_ParseTuple(args, "i", &is_visible)) 
    return NULL;  
  review_wdgt_set_answer_box_visible(is_visible);  
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject* _review_wdgt_set_question_label(PyObject* self, 
                                                 PyObject* args)
{
  char* text = NULL;
  if (!PyArg_ParseTuple(args, "s", &text))
    return NULL;
  review_wdgt_set_question_label(text);
  Py_INCREF(Py_None);
  return Py_None;
}
        

static PyObject* _review_wdgt_set_question(PyObject* self, PyObject* args)
{
  char* text = NULL;
  if (!PyArg_ParseTuple(args, "s", &text)) 
    return NULL;  
  review_wdgt_set_question(text);  
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _review_wdgt_set_answer(PyObject* self, PyObject* args)
{
  char* text = NULL;
  if (!PyArg_ParseTuple(args, "s", &text)) 
    return NULL;
  review_wdgt_set_answer(text); 
  Py_INCREF(Py_None);
  return Py_None;
}
        

static PyObject* _review_wdgt_clear_question(PyObject* self, PyObject* args)
{
  review_wdgt_clear_question(); 
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _review_wdgt_clear_answer(PyObject* self, PyObject* args)
{
  review_wdgt_clear_answer();  
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _review_wdgt_update_show_button(PyObject* self, 
                                                 PyObject* args)
{  
  char* text = NULL;
  int is_default = 0;
  int is_enabled = 0;
  if (!PyArg_ParseTuple(args, "sii", &text, &is_enabled, &is_default)) 
    return NULL;
  review_wdgt_update_show_button(text, is_enabled, is_default); 
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _review_wdgt_set_grades_enabled(PyObject* self, 
                                                 PyObject* args)
{
  int is_enabled = 0;
  if (!PyArg_ParseTuple(args, "i", &is_enabled))
    return NULL;
  review_wdgt_set_grades_enabled(is_enabled);
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _review_wdgt_set_grade_enabled(PyObject* self, PyObject* args)
{
  int grade = 0;
  int is_enabled = 0;  
  if (!PyArg_ParseTuple(args, "ii", &grade, &is_enabled)) 
    return NULL;
  review_wdgt_set_grade_enabled(grade, is_enabled);
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _review_wdgt_set_default_grade(PyObject* self, PyObject* args)
{
  int grade = 0;  
  if (!PyArg_ParseTuple(args, "i", &grade)) 
    return NULL;
  review_wdgt_set_default_grade(grade);
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _review_wdgt_set_grades_title(PyObject* self, PyObject* args)
{
  char* text = NULL;
  if (!PyArg_ParseTuple(args, "s", &text)) 
    return NULL;
  review_wdgt_set_grades_title(text);
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _review_wdgt_set_grade_text(PyObject* self, PyObject* args)
{
  int grade = 0;
  char* text = NULL; 
  if (!PyArg_ParseTuple(args, "is", &grade, &text)) 
    return NULL;
  review_wdgt_set_grade_text(grade, text);
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject* _review_wdgt_set_grade_tooltip(PyObject* self, PyObject* args)
{
  int grade = 0;
  char* text = NULL;
  if (!PyArg_ParseTuple(args, "is", &grade, &text)) 
    return NULL;
  review_wdgt_set_grade_tooltip(grade, text);
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _review_wdgt_update_status_bar_counters(PyObject* self, 
                                                         PyObject* args)
{
  review_wdgt_update_status_bar_counters();
  Py_INCREF(Py_None);
  return Py_None;
}


static PyMethodDef review_wdgt_methods[] = {
  {"set_question_box_visible",   _review_wdgt_set_question_box_visible, 
   METH_VARARGS, ""},
  {"set_answer_box_visible",     _review_wdgt_set_answer_box_visible, 
   METH_VARARGS, ""},
  {"set_question_label",         _review_wdgt_set_question_label, 
   METH_VARARGS, ""},
  {"set_question",               _review_wdgt_set_question, 
   METH_VARARGS, ""},
  {"set_answer",                 _review_wdgt_set_answer, 
   METH_VARARGS, ""},
  {"clear_question",             _review_wdgt_clear_question, 
   METH_VARARGS, ""},
  {"clear_answer",               _review_wdgt_clear_answer, 
   METH_VARARGS, ""},
  {"update_show_button",         _review_wdgt_update_show_button, 
   METH_VARARGS, ""},
  {"set_grades_enabled",         _review_wdgt_set_grades_enabled, 
   METH_VARARGS, ""},
  {"set_grade_enabled",          _review_wdgt_set_grade_enabled, 
   METH_VARARGS, ""},
  {"set_default_grade",          _review_wdgt_set_default_grade, 
   METH_VARARGS, ""},
  {"set_grades_title",           _review_wdgt_set_grades_title, 
   METH_VARARGS, ""},
  {"set_grade_text",             _review_wdgt_set_grade_text, 
   METH_VARARGS, ""},
  {"set_grade_tooltip",          _review_wdgt_set_grade_tooltip, 
   METH_VARARGS, ""},  
  {"update_status_bar_counters", _review_wdgt_update_status_bar_counters, 
   METH_VARARGS, ""},
  {NULL, NULL, 0, NULL}
};


PyMODINIT_FUNC
init__review_wdgt(void)
{
  Py_InitModule("_review_wdgt", review_wdgt_methods);
}



//
// Functions relating to capturing stdout and stderr.
//

PyObject* _python_stdout(PyObject* self, PyObject* pArgs)
{
  char* text = NULL;
  if (!PyArg_ParseTuple(pArgs, "s", &text)) 
    return NULL;
  python_stdout(text);
  Py_INCREF(Py_None);
  return Py_None;
}


PyObject* _python_stderr(PyObject* self, PyObject* pArgs)
{
  char* text = NULL;
  if (!PyArg_ParseTuple(pArgs, "s", &text)) 
    return NULL;
  python_stderr(text);
  Py_INCREF(Py_None);
  return Py_None;
}


static PyMethodDef python_stdout_stderr_methods[] = {
 {"python_stdout", _python_stdout, METH_VARARGS, ""},
 {"python_stderr", _python_stderr, METH_VARARGS, ""},
 {NULL, NULL, 0, NULL}
};


PyMODINIT_FUNC
init__python_stdout_stderr(void)
{
  Py_InitModule("_python_stdout_stderr", python_stdout_stderr_methods);
}



//
// High level functions.
//

void start_python_bridge()
{
  Py_Initialize();
  init__main_wdgt();
  init__review_wdgt();
  init__python_stdout_stderr();
  
  PyRun_SimpleString(
    "import sys\n"
    "import _python_stdout_stderr\n"
    "class StdoutCatcher:\n"
    "    def write(self, str):\n"
    "        _python_stdout_stderr.python_stdout(str)\n"
    "class StderrCatcher:\n"
    "    def write(self, str):\n"
    "        _python_stdout_stderr.python_stderr(str)\n"
    "sys.stdout = StdoutCatcher()\n"
    "sys.stderr = StderrCatcher()\n"
   );
}



void stop_python_bridge()
{
  Py_Finalize();
}


void run_python(char* command)
{
  PyRun_SimpleString(command);
}


void eval_python_as_unicode(char* expression, char* result, int bufsize)
{
  char buf[256];
  if (strlen(expression) + 26 > sizeof(buf))
  {
    printf("Expression too long in eval_as_unicode.\n");
    exit (-1);    
  };
  snprintf(buf, sizeof(buf), "unicode(%s).encode(\"utf-8\")", expression);
  PyObject* main = PyImport_AddModule("__main__");
  PyObject* main_dict = PyModule_GetDict(main);
  PyObject* obj = PyRun_String(buf, Py_eval_input, main_dict, main_dict);
  PyErr_Print();
  if (obj == NULL)
  {
    *result = NULL;
    return;
  }
  strncpy(result, PyString_AsString(obj), bufsize);
  Py_DECREF(obj);
}
