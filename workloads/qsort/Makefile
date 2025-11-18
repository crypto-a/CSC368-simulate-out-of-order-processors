FILE1 = qsort_small.c
FILE2 = qsort_large.c

all: qsort_small qsort_large

qsort_small: qsort_small.c Makefile
	gcc -static qsort_small.c -O3 -o qsort_small -lm -lm5 -I/u/csc368h/fall/pub/include -L/u/csc368h/fall/pub/lib
qsort_large: qsort_large.c Makefile
	gcc -static qsort_large.c -O3 -o qsort_large -lm -lm5 -I/u/csc368h/fall/pub/include -L/u/csc368h/fall/pub/lib

clean:
	rm -rf qsort_small qsort_large output*
