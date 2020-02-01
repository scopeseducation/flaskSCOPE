/*sd.c  C Program to Shutdown or Turn Off the Computer in Linux.*/
#include <stdio.h>
#include <stdlib.h>
int main()
{
  system("shutdown -P now");
  return 0;
}
