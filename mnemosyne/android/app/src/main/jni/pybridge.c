/**
    This file defines the JNI implementation of the PyBridge class.

    It implements the native methods of the class and makes sure that
    all the prints and errors from the Python interpreter is redirected
    to the Android log. This is specially useful as it allows us to
    debug the Python code running on the Android device using logcat.

*/

#include <Python.h>
#include <jni.h>
#include <android/log.h>

#define LOG(x) __android_log_write(ANDROID_LOG_INFO, "pybridge", (x))

/* --------------- */
/*   Android log   */
/* --------------- */

static PyObject *androidlog(PyObject *self, PyObject *args)
{
    char *str;
    if (!PyArg_ParseTuple(args, "s", &str))
        return NULL;

    LOG(str);
    Py_RETURN_NONE;
}


static PyMethodDef AndroidlogMethods[] = {
    {"log", androidlog, METH_VARARGS, "Logs to Android stdout"},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef AndroidlogModule = {
    PyModuleDef_HEAD_INIT,
    "androidlog",        /* m_name */
    "Log for Android",   /* m_doc */
    -1,                  /* m_size */
    AndroidlogMethods    /* m_methods */
};


PyMODINIT_FUNC PyInit_androidlog(void)
{
    return PyModule_Create(&AndroidlogModule);
}


void setAndroidLog()
{
    // Inject bootstrap code to redirect python stdin/stdout
    // to the androidlog module
    PyRun_SimpleString(
            "import sys\n" \
            "import androidlog\n" \
            "class LogFile(object):\n" \
            "    def __init__(self):\n" \
            "        self.buffer = ''\n" \
            "    def write(self, s):\n" \
            "        s = self.buffer + s\n" \
            "        lines = s.split(\"\\n\")\n" \
            "        for l in lines[:-1]:\n" \
            "            androidlog.log(l)\n" \
            "        self.buffer = lines[-1]\n" \
            "    def flush(self):\n" \
            "        return\n" \
            "sys.stdout = sys.stderr = LogFile()\n"
    );
}



/* ------------------ */
/*   Main widget      */
/* ------------------ */

/**
    Python module that calls back to the relevant Java functions.
*/

JavaVM* javaVM = NULL;
jclass activityClass;
jobject activityObj;
jmethodID answer_to_life_method;


static PyObject* _main_wdgt_show_question(PyObject* self, PyObject* args)
{
  char* text = NULL;
  char* option_0 = NULL;
  char* option_1 = NULL;
  char* option_2 = NULL;
  if (!PyArg_ParseTuple(args, "ssss", &text, &option_0, &option_1,
        &option_2))
    return NULL;

  // It is dangerous to store JNI env globally, so we do the following.
  // https://developer.vuforia.com/forum/faq/android-how-can-i-call-java-methods-c
  // Note that doing DetachCurrentThread later does not seem to be needed and in
  // fact complains about the VM still being running.
  JNIEnv *env;
  (*javaVM)->AttachCurrentThread(javaVM, &env, NULL);
  int result = 42; //(*env)->CallIntMethod(env, activityObj, answer_to_life_method);

  char str[500];
  sprintf(str, "Received %d in C from Java, using Python module", result);
  LOG(str);

  return Py_BuildValue("i", result);
}


static PyMethodDef _main_wdgt_methods[] = {
  {"show_question", _main_wdgt_show_question, METH_VARARGS, ""},
  {NULL, NULL, 0, NULL}
};


static struct PyModuleDef _main_widget_module = {
    PyModuleDef_HEAD_INIT,
    "_main_widget",      /* m_name */
    NULL,                /* m_doc */
    -1,                  /* m_size */
    _main_wdgt_methods   /* m_methods */
};


PyMODINIT_FUNC
PyInit__main_widget(void)
{
    return PyModule_Create(&_main_widget_module);
};



// TMP test function

int call_java(void) {
    // It is dangerous to store JNI env globally, so we do the following.
    // https://developer.vuforia.com/forum/faq/android-how-can-i-call-java-methods-c
    // Note that doing DetachCurrentThread later does not seem to be needed and in
    // fact complains about the VM still being running.
    JNIEnv *env;
    (*javaVM)->AttachCurrentThread(javaVM, &env, NULL);
    int result = 42; //(*env)->CallIntMethod(env, activityObj, answer_to_life_method);

    char str[250];
    sprintf(str, "Received %d in C from Java, no Python", result);
    LOG(str);

    LOG("End of call_java");
    return result;
}


/* ------------------------------------------- */
/*   Native methods to call Python from Java   */
/* ------------------------------------------- */

/**
    This function configures the location of the standard library,
    initializes the interpreter and sets up the python log redirect.
    It runs a file called bootstrap.py before returning, so make sure
    that you configure all your python code on that file.

    Note: the function must receives a string with the location of the
    python files extracted from the assets folder.

*/


JNIEXPORT jint JNICALL Java_org_mnemosyne_PyBridge_start
        (JNIEnv *env, jclass jc, jstring path, jobject activity)
{
    // Cache function pointers and objects.
    // https://developer.android.com/training/articles/perf-jni.html
    (*env)->GetJavaVM(env, &javaVM);
    activityObj = (*env)->NewGlobalRef(env, activity);
    jclass cls = (*env)->GetObjectClass(env, activity);
    activityClass = (jclass) (*env)->NewGlobalRef(env, cls);
    //answer_to_life_method = (*env)->GetMethodID(env, activityClass, "answer_to_life", "()I");

    // TMP TEST: Test call back.
    //call_java();

    LOG("Initializing the Python interpreter");

    // Get the location of the python files
    const char *pypath = (*env)->GetStringUTFChars(env, path, NULL);

    // Build paths for the Python interpreter
    char paths[512];
    snprintf(paths, sizeof(paths), "%s:%s/stdlib.zip", pypath, pypath);

    // Set Python paths
    wchar_t *wchar_paths = Py_DecodeLocale(paths, NULL);
    Py_SetPath(wchar_paths);

    // Initialize Python interpreter and other modules
    PyImport_AppendInittab("androidlog", PyInit_androidlog);
    PyImport_AppendInittab("_main_widget", PyInit__main_widget);
    Py_Initialize();
    setAndroidLog();

    // Bootstrap
	PyRun_SimpleString("import cmath");
	LOG("Imported cmath");
	 PyRun_SimpleString("import mnemosyne");
	LOG("Imported mnemosyne");
    PyRun_SimpleString("import mnemosyne.android_python.mnemosyne_android");
	LOG("Imported mnemosyne_android");

    // Cleanup
    (*env)->ReleaseStringUTFChars(env, path, pypath);
    PyMem_RawFree(wchar_paths);

    return 0;
}


JNIEXPORT jint JNICALL Java_org_mnemosyne_PyBridge_stop
        (JNIEnv *env, jclass jc)
{
    LOG("Trying to free global references");
    (*env)->DeleteGlobalRef(env, activityClass);
    (*env)->NewGlobalRef(env, activityObj);

    LOG("Finalizing the Python interpreter");
    Py_Finalize();
    return 0;
}


/**
    This function is responsible for receiving a payload string
    and sending it to the router function defined in the bootstrap.py
    file.

*/
JNIEXPORT jstring JNICALL Java_org_mnemosyne_PyBridge_call
        (JNIEnv *env, jclass jc, jstring payload)
{
    LOG("Call into Python interpreter");

    // Get the payload string
    jboolean iscopy;
    const char *payload_utf = (*env)->GetStringUTFChars(env, payload, &iscopy);

    // Import module
    PyObject* myModuleString = PyUnicode_FromString((char*)"bootstrap");
    PyObject* myModule = PyImport_Import(myModuleString);

    // Get reference to the router function
    PyObject* myFunction = PyObject_GetAttrString(myModule, (char*)"router");
    PyObject* args = PyTuple_Pack(1, PyUnicode_FromString(payload_utf));

    // Call function and get the resulting string
    PyObject* myResult = PyObject_CallObject(myFunction, args);
    char *myResultChar = PyUnicode_AsUTF8(myResult);

    // Store the result on a java.lang.String object
    jstring result = (*env)->NewStringUTF(env, myResultChar);

    // Cleanup
    (*env)->ReleaseStringUTFChars(env, payload, payload_utf);
    Py_DECREF(myModuleString);
    Py_DECREF(myModule);
    Py_DECREF(myFunction);
    Py_DECREF(args);
    Py_DECREF(myResult);

    return result;
}

