
//
// python_bridge.c <Peter.Bienstman@UGent.be>
//
 
#include <string.h>
#include <stdlib.h>
#include <Python.h>
#include "main_widget.h"

//
// Functions relating to main widget.
//

static PyObject* _main_widget_set_status_bar_message(PyObject* self, 
                                                     PyObject* args)
{
  char* message = NULL;
  if (!PyArg_ParseTuple(args, "s", &message))
    return NULL;

  // --------------------------------------------------------------------------
  // Replace this by something useful.
  printf("set_status_bar_message: %s\n", message);
  // --------------------------------------------------------------------------

  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _main_widget_show_information(PyObject* self, 
                                               PyObject* args)
{
  char* message = NULL;
  if (!PyArg_ParseTuple(args, "s", &message)) 
    return NULL;

  // --------------------------------------------------------------------------
  // Replace this by something useful.
  printf("show_information: %s\n", message);
  // --------------------------------------------------------------------------

  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _main_widget_show_question(PyObject* self, 
                                            PyObject* args)
{
  char* question = NULL;
  char* option_0 = NULL;
  char* option_1 = NULL;
  char* option_2 = NULL;
  if (!PyArg_ParseTuple(args, "ssss", &question, &option_0, &option_1,
        &option_2)) 
    return NULL;
  int answer;
  answer = main_widget_show_question(question, option_0, option_1,
                                     option_2);
  return Py_BuildValue("i", answer);
}


static PyObject* _main_widget_show_error(PyObject* self, 
                                         PyObject* args)
{
  char* message = NULL;
  if (!PyArg_ParseTuple(args, "s", &message)) 
    return NULL;

  // --------------------------------------------------------------------------
  // Replace this by something useful.
  printf("show_error: %s\n", message);
  // --------------------------------------------------------------------------

  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _main_widget_set_progress_text(PyObject* self, 
                                                PyObject* args)
{
  char* text = NULL;
  if (!PyArg_ParseTuple(args, "s", &text)) 
    return NULL;

  // --------------------------------------------------------------------------
  // Replace this by something useful.
  printf("set_progress_text: %s\n", text);
  // --------------------------------------------------------------------------

  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _main_widget_set_progress_range(PyObject* self, 
                                                 PyObject* args)
{
  int min=0;
  int max=0;
  if (!PyArg_ParseTuple(args, "ii", &min, &max)) 
    return NULL;

  // --------------------------------------------------------------------------
  // Replace this by something useful.
  printf("set_progress_range: %d %d\n", min, max);
  // --------------------------------------------------------------------------

  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _main_widget_set_progress_update_interval(PyObject* self, 
                                                           PyObject* args)
{
  int interval=0;
  if (!PyArg_ParseTuple(args, "i", &interval)) 
    return NULL;

  // --------------------------------------------------------------------------
  // Replace this by something useful.
  printf("set_progress_update_interval: %d\n", interval);
  // --------------------------------------------------------------------------

  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _main_widget_set_progress_value(PyObject* self, 
                                                 PyObject* args)
{
  int value=0;
  if (!PyArg_ParseTuple(args, "i", &value)) 
    return NULL;

  // --------------------------------------------------------------------------
  // Replace this by something useful.
  printf("set_progress_value: %d\n", value);
  // --------------------------------------------------------------------------

  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _main_widget_close_progress(PyObject* self, 
                                             PyObject* args)
{
  // --------------------------------------------------------------------------
  // Replace this by something useful.
  printf("close_progress\n");
  // --------------------------------------------------------------------------

  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _main_widget_enable_edit_current_card(PyObject* self, 
                                                       PyObject* args)
{
 int enable=0;
 if (!PyArg_ParseTuple(args, "i", &enable)) 
   return NULL;

 // --------------------------------------------------------------------------
 // Replace this by something useful.
 printf("enable_edit_current_card: %d\n", enable);
 // --------------------------------------------------------------------------

 Py_INCREF(Py_None);
 return Py_None;
}


static PyObject* _main_widget_enable_delete_current_card(PyObject* self, 
                                                         PyObject* args)
{
 int enable=0;
 if (!PyArg_ParseTuple(args, "i", &enable)) 
   return NULL;

 // --------------------------------------------------------------------------
 // Replace this by something useful.
 printf("enable_delete_current_card: %d\n", enable);
 // --------------------------------------------------------------------------

 Py_INCREF(Py_None);
 return Py_None;
}


static PyObject* _main_widget_enable_browse_cards(PyObject* self, 
                                                  PyObject* args)
{
 int enable=0;
 if (!PyArg_ParseTuple(args, "i", &enable)) 
   return NULL;

 // --------------------------------------------------------------------------
 // Replace this by something useful.
 printf("enable_browse_cards: %d\n", enable);
 // --------------------------------------------------------------------------

 Py_INCREF(Py_None);
 return Py_None;
}


static PyObject* _main_widget_get_filename_to_save(PyObject* self, 
                                                   PyObject* args)
{
  char* path = NULL;
  char* filter = NULL;
  char* caption = NULL;
  if (!PyArg_ParseTuple(args, "sss", &path, &filter, &caption))
    return NULL;

  // --------------------------------------------------------------------------
  // Replace this by something useful.
  printf("get_filename_to_save: %s, %s, %s\n", path, filter, caption);
  // We should ask the user which path he chooses, but here, we just 
  // hardcode 'tmp'.
  char answer[5] = "tmp";
  // --------------------------------------------------------------------------
  return PyUnicode_FromString(answer);
}


static PyObject* _main_widget_get_filename_to_open(PyObject* self, 
                                                   PyObject* args)
{
  char* path = NULL;
  char* filter = NULL;
  char* caption = NULL;
  if (!PyArg_ParseTuple(args, "sss", &path, &filter, &caption))
    return NULL;

  // --------------------------------------------------------------------------
  // Replace this by something useful.
  printf("get_filename_to_open: %s, %s, %s\n", path, filter, caption);
  // We should ask the user which path he chooses, but here, we just 
  // hardcode 'tmp'.
  char answer[5] = "tmp";
  // --------------------------------------------------------------------------
  return PyUnicode_FromString(answer);
}


static PyObject* _main_widget_set_window_title(PyObject* self, 
                                               PyObject* args)
{
 char* title = NULL;
 if (!PyArg_ParseTuple(args, "s", &title)) 
   return NULL;

 // --------------------------------------------------------------------------
 // Replace this by something useful.
 printf("set_window_title: %s\n", title);
 // --------------------------------------------------------------------------

 Py_INCREF(Py_None);
 return Py_None;
}


static PyMethodDef C_main_widget_methods[] = {
 {"set_window_title",             _main_widget_set_window_title, 
  METH_VARARGS, ""},
 {"show_information",             _main_widget_show_information, 
  METH_VARARGS, ""},
 {"show_question",                _main_widget_show_question, 
  METH_VARARGS, ""},
 {"show_error",                   _main_widget_show_error, 
  METH_VARARGS, ""},
 {"get_filename_to_open",         _main_widget_get_filename_to_open, 
  METH_VARARGS, ""},
 {"get_filename_to_save",         _main_widget_get_filename_to_save, 
  METH_VARARGS, ""},
 {"set_status_bar_message",       _main_widget_set_status_bar_message, 
  METH_VARARGS, ""},
 {"set_progress_text",            _main_widget_set_progress_text, 
  METH_VARARGS, ""},
 {"set_progress_range",           _main_widget_set_progress_range, 
  METH_VARARGS, ""},
 {"set_progress_update_interval", _main_widget_set_progress_update_interval, 
  METH_VARARGS, ""},
 {"set_progress_value",           _main_widget_set_progress_value, 
  METH_VARARGS, ""},
 {"close_progress",               _main_widget_close_progress, 
  METH_VARARGS, ""},
 {"enable_edit_current_card",     _main_widget_enable_edit_current_card, 
  METH_VARARGS, ""},
 {"enable_delete_current_card",   _main_widget_enable_delete_current_card, 
  METH_VARARGS, ""},
 {"enable_browse_cards",          _main_widget_enable_browse_cards, 
  METH_VARARGS, ""},
 {NULL, NULL, 0, NULL}
};


PyMODINIT_FUNC
init_C_main_widget(void)
{
  Py_InitModule("_C_main_widget", C_main_widget_methods);
}



//
// High level functions.
//


PyObject* log_CaptureStdout(PyObject* self, PyObject* pArgs)
{
 char* LogStr = NULL;
 if (!PyArg_ParseTuple(pArgs, "s", &LogStr)) 
   return NULL;

 printf("%s", LogStr);

 Py_INCREF(Py_None);
 return Py_None;
}


PyObject* log_CaptureStderr(PyObject* self, PyObject* pArgs)
{
 char* LogStr = NULL;
 if (!PyArg_ParseTuple(pArgs, "s", &LogStr)) 
   return NULL;

 printf("%s", LogStr);

 Py_INCREF(Py_None);
 return Py_None;
}

static PyMethodDef logMethods[] = {
 {"CaptureStdout", log_CaptureStdout, METH_VARARGS, "Logs stdout"},
 {"CaptureStderr", log_CaptureStderr, METH_VARARGS, "Logs stderr"},
 {NULL, NULL, 0, NULL}
};


void start_python_bridge()
{
  Py_Initialize();
  Py_InitModule("log", logMethods);
  
  init_C_main_widget();
  
  PyRun_SimpleString(
    "import log\n"
    "import sys\n"
    "class StdoutCatcher:\n"
    "\tdef write(self, str):\n"
    "\t\tlog.CaptureStdout(str)\n"
    "class StderrCatcher:\n"
    "\tdef write(self, str):\n"
    "\t\tlog.CaptureStderr(str)\n"
    "sys.stdout = StdoutCatcher()\n"
    "sys.stderr = StderrCatcher()\n"
   );
}


void stop_python_bridge()
{
  Py_Finalize();
}


void eval_python_as_unicode(char* expression, char* result, int bufsize)
{
  char buf[256];
  if (strlen(expression) + 10 > sizeof(buf))
  {
    printf("Expression too long in eval_as_unicode.\n");
    exit (-1);    
  };
  snprintf(buf, sizeof(buf), "unicode(%s)", expression);

  PyObject* module = PyImport_ImportModule("__builtin__");
  PyObject* obj = PyRun_String(buf, Py_eval_input, PyModule_GetDict(module), NULL);
  Py_DECREF(module);
  PyErr_Print();
  strncpy(result, PyString_AsString(obj), bufsize);
  Py_DECREF(obj);
}
