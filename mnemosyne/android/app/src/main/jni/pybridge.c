/**
    This file defines the JNI implementation of the PyBridge class.

    It implements the native methods of the class and makes sure that
    all the prints and errors from the Python interpreter is redirected
    to the Android log. This is specially useful as it allows us to
    debug the Python code running on the Android device using logcat.

*/

#define STR_SIZE 128

#include <string.h>
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
/*  Cached variables  */
/* ------------------ */

JavaVM* javaVM = NULL;

jclass threadClass;
jobject threadObj;

/* ------------------ */
/*  Main widget       */
/* ------------------ */

jmethodID _main_wdgt_set_window_title_method;
jmethodID _main_wdgt_show_information_method;
jmethodID _main_wdgt_show_question_method;
jmethodID _main_wdgt_show_error_method;
jmethodID _main_wdgt_get_filename_to_open_method;
jmethodID _main_wdgt_get_filename_to_save_method;
jmethodID _main_wdgt_set_status_bar_message_method;
jmethodID _main_wdgt_set_progress_text_method;
jmethodID _main_wdgt_set_progress_range_method;
jmethodID _main_wdgt_set_progress_update_interval_method;
jmethodID _main_wdgt_set_progress_value_method;
jmethodID _main_wdgt_close_progress_method;
jmethodID _main_wdgt_enable_edit_current_card_method;
jmethodID _main_wdgt_enable_delete_current_card_method;
jmethodID _main_wdgt_enable_browse_cards_method;

static PyObject* _main_wdgt_set_window_title(PyObject* self, PyObject* args)
{
  char* text = NULL;
  if (!PyArg_ParseTuple(args, "s", &text))
    return NULL;
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
  (*env)->CallVoidMethod(env, threadObj,
    _main_wdgt_set_window_title_method, text);
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _main_wdgt_show_information(PyObject* self, PyObject* args)
{
  char* text = NULL;
  if (!PyArg_ParseTuple(args, "s", &text))
    return NULL;
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
  (*env)->CallVoidMethod(env, threadObj,
    _main_wdgt_show_information_method, text);
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
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
  int answer;
  answer = (*env)->CallIntMethod(env, threadObj,
    _main_widget_show_question_method, text, option_0, option_1, option_2);
  return Py_BuildValue("i", result);
}


static PyObject* _main_wdgt_show_error(PyObject* self, PyObject* args)
{
  char* text = NULL;
  if (!PyArg_ParseTuple(args, "s", &text))
    return NULL;
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
  (*env)->CallVoidMethod(env, threadObj,
    _main_wdgt_show_error_method, text);
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
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
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
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
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
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
  main_wdgt_set_status_bar_message(text);
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _main_wdgt_set_progress_text(PyObject* self, PyObject* args)
{
  char* text = NULL;
  if (!PyArg_ParseTuple(args, "s", &text))
    return NULL;
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
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
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
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
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
  main_wdgt_set_progress_update_interval(interval);
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _main_wdgt_set_progress_value(PyObject* self, PyObject* args)
{
  int value = 0;
  if (!PyArg_ParseTuple(args, "i", &value))
    return NULL;
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
  main_wdgt_set_progress_value(value);
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _main_wdgt_close_progress(PyObject* self, PyObject* args)
{
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
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
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
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
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
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
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
  main_wdgt_enable_browse_cards(is_enabled);
  Py_INCREF(Py_None);
  return Py_None;
}


static PyMethodDef _main_wdgt_methods[] = {
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

/* ------------------ */
/*  Review widget     */
/* ------------------ */

jmethodID _review_wdgt_set_question_box_visible_method;
jmethodID _review_wdgt_set_answer_box_visible_method;
jmethodID _review_wdgt_set_question_label_method;
jmethodID _review_wdgt_set_question_method;
jmethodID _review_wdgt_set_answer_method;
jmethodID _review_wdgt_clear_question_method;
jmethodID _review_wdgt_clear_answer_method;
jmethodID _review_wdgt_update_show_button_method;
jmethodID _review_wdgt_set_grades_enabled_method;
jmethodID _review_wdgt_set_grade_enabled_method;
jmethodID _review_wdgt_set_default_grade_method;
jmethodID _review_wdgt_set_grades_title_method;
jmethodID _review_wdgt_set_grade_text_method;
jmethodID _review_wdgt_set_grade_tooltip_method;
jmethodID _review_wdgt_update_status_bar_counters_method;
jmethodID _review_wdgt_redraw_now_method;

static PyObject* _review_wdgt_set_question_box_visible(PyObject* self,
                                                       PyObject* args)
{
  int is_visible = 0;
  if (!PyArg_ParseTuple(args, "i", &is_visible))
    return NULL;
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
  (*env)->CallVoidMethod(env, threadObj,
    _review_wdgt_set_question_box_visible_method, is_visible);
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _review_wdgt_set_answer_box_visible(PyObject* self,
						     PyObject* args)
{
  int is_visible = 0;
  if (!PyArg_ParseTuple(args, "i", &is_visible))
    return NULL;
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
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
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
  review_wdgt_set_question_label(text);
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _review_wdgt_set_question(PyObject* self, PyObject* args)
{
  char* text = NULL;
  if (!PyArg_ParseTuple(args, "s", &text))
    return NULL;
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
  review_wdgt_set_question(text);
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _review_wdgt_set_answer(PyObject* self, PyObject* args)
{
  char* text = NULL;
  if (!PyArg_ParseTuple(args, "s", &text))
    return NULL;
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
  review_wdgt_set_answer(text);
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _review_wdgt_clear_question(PyObject* self, PyObject* args)
{
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
  review_wdgt_clear_question();
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _review_wdgt_clear_answer(PyObject* self, PyObject* args)
{
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
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
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
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
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
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
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
  review_wdgt_set_grade_enabled(grade, is_enabled);
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _review_wdgt_set_default_grade(PyObject* self, PyObject* args)
{
  int grade = 0;
  if (!PyArg_ParseTuple(args, "i", &grade))
    return NULL;
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
  review_wdgt_set_default_grade(grade);
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _review_wdgt_set_grades_title(PyObject* self, PyObject* args)
{
  char* text = NULL;
  if (!PyArg_ParseTuple(args, "s", &text))
    return NULL;
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
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
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
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
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
  review_wdgt_set_grade_tooltip(grade, text);
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _review_wdgt_update_status_bar_counters(PyObject* self,
							 PyObject* args)
{
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
  review_wdgt_update_status_bar_counters();
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject* _review_wdgt_redraw_now(PyObject* self, PyObject* args)
{
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
  review_wdgt_redraw_now();
  Py_INCREF(Py_None);
  return Py_None;
}


static PyMethodDef _review_wdgt_methods[] = {
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
  {"redraw_now",                 _review_wdgt_redraw_now,
   METH_VARARGS, ""},
  {NULL, NULL, 0, NULL}
};


static struct PyModuleDef _review_widget_module = {
    PyModuleDef_HEAD_INIT,
    "_review_widget",    /* m_name */
    NULL,                /* m_doc */
    -1,                  /* m_size */
    _review_wdgt_methods /* m_methods */
};


PyMODINIT_FUNC
PyInit__review_widget(void)
{
    return PyModule_Create(&_review_widget_module);
};

/* ------------------ */
/*  Dialogs           */
/* ------------------ */

jmethodID _add_cards_dlg_activate_method;
jmethodID _edit_card_dlg_activate_method;
jmethodID _activate_cards_dlg_activate_method;
jmethodID _browse_cards_dlg_activate_method;
jmethodID _card_appearance_dlg_activate_method;
jmethodID _activate_plugins_dlg_activate_method;
jmethodID _manage_card_types_dlg_activate_method;
jmethodID _statistics_dlg_activate_method;
jmethodID _configuration_dlg_activate_method;
jmethodID _sync_dlg_activate_method;

PyObject* _add_cards_dlg_activate(PyObject* self, PyObject* args)
{
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
  add_cards_dlg_activate();
  Py_INCREF(Py_None);
  return Py_None;
}


PyObject* _edit_card_dlg_activate(PyObject* self, PyObject* args)
{
  char* card_id = NULL;
  int allow_cancel = 1;
  if (!PyArg_ParseTuple(args, "si", &card_id, &allow_cancel))
    return NULL;
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
  edit_card_dlg_activate(card_id, allow_cancel);
  Py_INCREF(Py_None);
  return Py_None;
}


PyObject* _activate_cards_dlg_activate(PyObject* self, PyObject* args)
{
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
  activate_cards_dlg_activate();
  Py_INCREF(Py_None);
  return Py_None;
}


PyObject* _browse_cards_dlg_activate(PyObject* self, PyObject* args)
{
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
  browse_cards_dlg_activate();
  Py_INCREF(Py_None);
  return Py_None;
}


PyObject* _card_appearance_dlg_activate(PyObject* self, PyObject* args)
{
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
  card_appearance_dlg_activate();
  Py_INCREF(Py_None);
  return Py_None;
}


PyObject* _activate_plugins_dlg_activate(PyObject* self, PyObject* args)
{
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
  activate_plugins_dlg_activate();
  Py_INCREF(Py_None);
  return Py_None;
}


PyObject* _manage_card_types_dlg_activate(PyObject* self, PyObject* args)
{
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
  manage_card_types_dlg_activate();
  Py_INCREF(Py_None);
  return Py_None;
}


PyObject* _statistics_dlg_activate(PyObject* self, PyObject* args)
{
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
  statistics_dlg_activate();
  Py_INCREF(Py_None);
  return Py_None;
}


PyObject* _configuration_dlg_activate(PyObject* self, PyObject* args)
{
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
  configuration_dlg_activate();
  Py_INCREF(Py_None);
  return Py_None;
}


PyObject* _sync_dlg_activate(PyObject* self, PyObject* args)
{
  JNIEnv *env;
  (*javaVM)->GetEnv(javaVM, (void **) &env, JNI_VERSION_1_6);
  sync_dlg_activate();
  Py_INCREF(Py_None);
  return Py_None;
}

static struct PyModuleDef _dialogs_module = {
    PyModuleDef_HEAD_INIT,
    "_dialogs",          /* m_name */
    NULL,                /* m_doc */
    -1,                  /* m_size */
    _review_wdgt_methods /* m_methods */
};


PyMODINIT_FUNC
PyInit__dialogs(void)
{
    return PyModule_Create(&_dialogs_module);
};

/* ------------------------------------------- */
/*   Native methods to call Python from Java   */
/* ------------------------------------------- */

/**
    This function configures the location of the standard library,
    initializes the interpreter and sets up the python log redirect.
    It runs a file called bootstrap.py before returning, so make sure
    that you configure all your python code on that file.

    Note: the function must receive a string with the location of the
    python files extracted from the assets folder.

*/


JNIEXPORT jint JNICALL Java_org_mnemosyne2_PyBridge_start
        (JNIEnv *env, jclass jc, jstring path, jobject thread)
{
    // Cache function pointers and objects.
    // https://developer.android.com/training/articles/perf-jni.html
    (*env)->GetJavaVM(env, &javaVM);
	threadObj = (*env)->NewGlobalRef(env, thread);
    jclass cls = (*env)->GetObjectClass(env, thread);
	threadClass = (jclass) (*env)->NewGlobalRef(env, cls);

    set_question_box_visible_method = (*env)->GetMethodID(env, threadClass,
		"setQuestionBoxVisible", "(Z)V");

    //char str[250];
    //sprintf(str, "Method ID: %p ", set_question_box_visible_method);
    //LOG(str);

    LOG("Initializing the Python interpreter");

    // Get the location of the python files.
    const char *pypath = (*env)->GetStringUTFChars(env, path, NULL);

    // Build paths for the Python interpreter.
    char paths[512];
    snprintf(paths, sizeof(paths), "%s:%s/stdlib.zip:%s/mnemosyne.zip",
	pypath, pypath, pypath);

    // Set Python paths.
    wchar_t *wchar_paths = Py_DecodeLocale(paths, NULL);
    Py_SetPath(wchar_paths);

    // Initialize Python interpreter and other modules.
    PyImport_AppendInittab("androidlog", PyInit_androidlog);
    PyImport_AppendInittab("_main_widget", PyInit__main_widget);
    PyImport_AppendInittab("_review_widget", PyInit__review_widget);
      PyImport_AppendInittab("_dialogs", PyInit__dialogs);
    Py_Initialize();
    setAndroidLog();

    // Bootstrap.
    PyRun_SimpleString("import bootstrap");

    // Clean up.
    (*env)->ReleaseStringUTFChars(env, path, pypath);
    PyMem_RawFree(wchar_paths);

    return 0;
}


JNIEXPORT jint JNICALL Java_org_mnemosyne2_PyBridge_stop
        (JNIEnv *env, jclass jc)
{
    LOG("Trying to free global references");
    (*env)->DeleteGlobalRef(env, threadClass);
    (*env)->NewGlobalRef(env, threadObj);

    LOG("Finalizing the Python interpreter");
    Py_Finalize();
    return 0;
}


/**
    This function is responsible for receiving a payload string
    and sending it to the router function defined in the bootstrap.py
    file.

*/
JNIEXPORT jstring JNICALL Java_org_mnemosyne2_PyBridge_call
        (JNIEnv *env, jclass jc, jstring payload)
{
    LOG("Call into Python interpreter");

    // Get the payload string.
    jboolean iscopy;
    const char *payload_utf = (*env)->GetStringUTFChars(env, payload, &iscopy);

    // Import module.
    PyObject* myModuleString = PyUnicode_FromString((char*)"bootstrap");
    PyObject* myModule = PyImport_Import(myModuleString);

    // Get reference to the router function.
    PyObject* myFunction = PyObject_GetAttrString(myModule, (char*)"router");
    PyObject* args = PyTuple_Pack(1, PyUnicode_FromString(payload_utf));

    // Call function and get the resulting string.
    PyObject* myResult = PyObject_CallObject(myFunction, args);
    char *myResultChar = PyUnicode_AsUTF8(myResult);

    // Store the result on a java.lang.String object.
    jstring result = (*env)->NewStringUTF(env, myResultChar);

    // Cleanup.
    (*env)->ReleaseStringUTFChars(env, payload, payload_utf);
    Py_DECREF(myModuleString);
    Py_DECREF(myModule);
    Py_DECREF(myFunction);
    Py_DECREF(args);
    Py_DECREF(myResult);

    return result;
}

