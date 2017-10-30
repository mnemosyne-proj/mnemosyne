//
// python_stdout_stderr.c <Peter.Bienstman@UGent.be>
//

#include <stdio.h>

void python_stdout(char* text)
{
  printf("%s", text);
}


void python_stderr(char* text)
{
  printf("%s", text);
}
