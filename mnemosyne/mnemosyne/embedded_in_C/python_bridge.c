//
// python_bridge.c <Peter.Bienstman@UGent.be>
//
 
#include <string.h>
#include <stdlib.h>
#include <Python.h>

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
