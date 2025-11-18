FILE = bitcnt_1.c bitcnt_2.c bitcnt_3.c bitcnt_4.c bitcnts.c bitfiles.c bitstrng.c bstr_i.c 

bitcnts: ${FILE} Makefile
	gcc -static ${FILE} -O3 -o bitcnts -lm5 -I/u/csc368h/fall/pub/include -L/u/csc368h/fall/pub/lib

clean:
	rm -rf bitcnts output*
