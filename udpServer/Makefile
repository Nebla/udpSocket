CC=gcc
CFLAGS = -g 

all: udp-send udp-recv

udp-send: udp-send.o 
	$(CC) -o udp-send udp-send.o $(LIBS)

udp-recv: udp-recv.o 
	$(CC) -o udp-recv udp-recv.o $(LIBS)

udp-send.o: udp-send.c

udp-recv.o: udp-recv.c

clean:
	rm -f udp-send udp-recv udp-send.o udp-recv.o 
