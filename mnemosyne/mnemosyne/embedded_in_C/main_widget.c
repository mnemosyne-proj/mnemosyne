// main_widget.c <Peter.Bienstman@UGent.be>

#include <Python.h>

static PyObject* _set_window_title(PyObject* self, PyObject* args)
{
 char* title = NULL;
 if (!PyArg_ParseTuple(args, "s", &title)) 
   return NULL;

 // ----------------------------------------------------------------
 // Replace this by something useful.
 printf("set_window_title: %s\n", title);
 // ----------------------------------------------------------------

 Py_INCREF(Py_None);
 return Py_None;
}

static PyMethodDef main_widget_methods[] = {
 {"_set_window_title", _set_window_title, METH_VARARGS, "_set_window_title"},
 {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
init_C_main_widget(void)
{
  Py_InitModule("_C_main_widget", main_widget_methods);
}
