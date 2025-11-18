all:  dijkstra_large dijkstra_small

dijkstra_large: dijkstra_large.c Makefile
	gcc -static dijkstra_large.c -O3 -o dijkstra_large -lm5 -I/u/csc368h/fall/pub/include -L/u/csc368h/fall/pub/lib

dijkstra_small: dijkstra_small.c Makefile
	gcc -static dijkstra_small.c -O3 -o dijkstra_small -lm5 -I/u/csc368h/fall/pub/include -L/u/csc368h/fall/pub/lib

clean:
	rm -rf dijkstra_large dijkstra_small output*
