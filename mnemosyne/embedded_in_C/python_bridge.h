//
// python_bridge.h <Peter.Bienstman@gmail.com>
//

void start_python_bridge();

void run_python(char* command);

// Evaluates a Python expression and returns the result as a unicode string
// encoded in utf-8.
// The caller has ownership of the 'result' buffer.
void eval_python_as_unicode(char* expression, char* result, int bufsize);

void stop_python_bridge();

