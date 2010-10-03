// main_widget.c <Peter.Bienstman@UGent.be>

#include <Python.h>

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
 printf("show question: %s, %s, %s, %s\n", question, option_0, option_1,
        option_2);
 // We should ask the user which option he chooses, but here, we just 
 // hardcode option 0.
 int answer = 0;
 // --------------------------------------------------------------------------
 return Py_BuildValue("i", answer);

}

static PyMethodDef main_widget_methods[] = {
 {"_set_window_title", _set_window_title, METH_VARARGS, ""},
 {"_show_question", _show_question, METH_VARARGS, ""},
 {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
init_C_main_widget(void)
{
  Py_InitModule("_C_main_widget", main_widget_methods);
}
