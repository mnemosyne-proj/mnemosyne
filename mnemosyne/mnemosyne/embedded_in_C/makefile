CC	= gcc
CFLAGS	= -O -I/usr/include/python2.6
LD	= $(CC)
LDFLAGS	= -lpython2.6
RM	= rm

EXE	= mnemosyne
SRCS = python_bridge.c main_widget.c review_widget.c mnemosyne.c 
OBJS = ${SRCS:.c=.o}

.c.o :
	$(CC) $(CFLAGS) -c $<

all : $(EXE)

$(EXE) : $(OBJS)
	$(LD) $(LDFLAGS) -o $@ $(OBJS)

$(OBJS) : python_bridge.h main_widget.h review_widget.h

clean :
	-$(RM) -f $(EXE) $(OBJS)
