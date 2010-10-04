// main_widget.c <Peter.Bienstman@UGent.be>

#include <Python.h>

static PyObject* _set_status_bar_message(PyObject* self, PyObject* args)
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


static PyObject* _show_information(PyObject* self, PyObject* args)
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


static PyObject* _show_question(PyObject* self, PyObject* args)
{
  char* question = NULL;
  char* option_0 = NULL;
  char* option_1 = NULL;
  char* option_2 = NULL;
  if (!PyArg_ParseTuple(args, "ssss", &question, &option_0, &option_1,
        &option_2)) 
    return NULL;

  // --------------------------------------------------------------------------
  // Replace this by something useful.
  printf("show_question: %s, %s, %s, %s\n", question, option_0, option_1,
         option_2);
  // We should ask the user which option he chooses, but here, we just 
  // hardcode option 0.
  int answer = 0;
  // --------------------------------------------------------------------------
  return Py_BuildValue("i", answer);
}


static PyObject* _show_error(PyObject* self, PyObject* args)
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


static PyObject* _set_progress_text(PyObject* self, PyObject* args)
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


static PyObject* _set_progress_range(PyObject* self, PyObject* args)
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


static PyObject* _set_progress_update_interval(PyObject* self, PyObject* args)
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


static PyObject* _set_progress_value(PyObject* self, PyObject* args)
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


static PyObject* _close_progress(PyObject* self, PyObject* args)
{
  // --------------------------------------------------------------------------
  // Replace this by something useful.
  printf("close_progress\n");
  // --------------------------------------------------------------------------

  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _enable_edit_current_card(PyObject* self, PyObject* args)
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


static PyObject* _enable_delete_current_card(PyObject* self, PyObject* args)
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


static PyObject* _enable_browse_cards(PyObject* self, PyObject* args)
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


static PyObject* _show_save_file_dialog(PyObject* self, PyObject* args)
{
  char* path = NULL;
  char* filter = NULL;
  char* caption = NULL;
  if (!PyArg_ParseTuple(args, "sss", &path, &filter, &caption))
    return NULL;

  // --------------------------------------------------------------------------
  // Replace this by something useful.
  printf("show_save_file_dialog: %s, %s, %s\n", path, filter, caption);
  // We should ask the user which path he chooses, but here, we just 
  // hardcode 'tmp'.
  char answer[5] = "tmp";
  // --------------------------------------------------------------------------
  return Py_BuildValue("s", answer);
}


static PyObject* _show_open_file_dialog(PyObject* self, PyObject* args)
{
  char* path = NULL;
  char* filter = NULL;
  char* caption = NULL;
  if (!PyArg_ParseTuple(args, "sss", &path, &filter, &caption))
    return NULL;

  // --------------------------------------------------------------------------
  // Replace this by something useful.
  printf("show_open_file_dialog: %s, %s, %s\n", path, filter, caption);
  // We should ask the user which path he chooses, but here, we just 
  // hardcode 'tmp'.
  char answer[5] = "tmp";
  // --------------------------------------------------------------------------
  return Py_BuildValue("s", answer);
}


static PyObject* _set_window_title(PyObject* self, PyObject* args)
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


static PyMethodDef main_widget_methods[] = {

 {"_set_status_bar_message", _set_status_bar_message, METH_VARARGS, ""},
 {"_show_information", _show_information, METH_VARARGS, ""},
 {"_show_question", _show_question, METH_VARARGS, ""},
 {"_show_error", _show_error, METH_VARARGS, ""},
 {"_set_progress_text", _set_progress_text, METH_VARARGS, ""},
 {"_set_progress_range", _set_progress_range, METH_VARARGS, ""},
 {"_set_progress_update_interval", _set_progress_update_interval, METH_VARARGS, ""},
 {"_set_progress_value", _set_progress_value, METH_VARARGS, ""},
 {"_close_progress", _close_progress, METH_VARARGS, ""},
 {"_enable_edit_current_card", _enable_edit_current_card, METH_VARARGS, ""},
 {"_enable_delete_current_card", _enable_delete_current_card, METH_VARARGS, ""},
 {"_enable_browse_cards", _enable_browse_cards, METH_VARARGS, ""},
 {"_show_save_file_dialog", _show_save_file_dialog, METH_VARARGS, ""},
 {"_show_open_file_dialog", _show_open_file_dialog, METH_VARARGS, ""},
 {"_set_window_title", _set_window_title, METH_VARARGS, ""},
 {NULL, NULL, 0, NULL}
};


PyMODINIT_FUNC
init_C_main_widget(void)
{
  Py_InitModule("_C_main_widget", main_widget_methods);
}
