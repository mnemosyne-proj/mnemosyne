// mnemosyne.c <Peter.Bienstman@UGent.be>

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

// Notice we have STDERR too.
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

void init_C_main_widget(void); /* Forward */


// Evaluates a Python expression and returns the result as a unicode string
// encoded in the system's default encoding.
// The caller has ownership of the 'result' buffer.

void eval_as_unicode(char* expression, char* result, int bufsize)
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


int main(int argc, char *argv[])
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

  PyRun_SimpleString(
    "import sys\n"
    "sys.path.insert(0, \"/home/pbienst/source/mnemosyne-proj-pbienst/mnemosyne\")\n"
    "sys.path.insert(0, \"/home/pbienst/source/mnemosyne-proj-pbienst/mnemosyne-proj/mnemosyne\")\n"
    "from mnemosyne.libmnemosyne import Mnemosyne\n"
    "mnemosyne = Mnemosyne()\n"
    "mnemosyne.components.insert(0, (\"mnemosyne.libmnemosyne.translator\", \"GetTextTranslator\"))\n"
    "mnemosyne.components.append((\"mnemosyne.embedded_in_C.C_main_widget\", \"C_MainWidget\"))\n"
    "mnemosyne.components.append((\"mnemosyne.embedded_in_C.C_review_widget\", \"C_ReviewWidget\"))\n"
    "mnemosyne.initialise(data_dir=\"/home/pbienst/source/mnemosyne-proj-pbienst/mnemosyne/dot_mnemosyne2\", filename=\"default.db\")\n"
    "mnemosyne.config()[\"upload_science_logs\"] = False\n"
    "mnemosyne.main_widget().show_question(\"q\", \"0\",\"1\")\n"    
    "mnemosyne.main_widget().show_save_file_dialog(\"q\", \"0\",\"1\")\n"
    "mnemosyne.main_widget().enable_edit_current_card(False)\n"
);

  // Illustration on how to get data from Python to C.

  char result[256];
  eval_as_unicode("1", result, sizeof(result));
  printf("result as string: %s\n", result);

  Py_Finalize();
  return 0;
}
