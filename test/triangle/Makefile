all: 
	$(MAKE) top_triangle_generator 
	$(MAKE) wave_generator 
	$(MAKE) tb

top_triangle_generator: clean
	make -f makefile.top_triangle_generator

wave_generator: clean
	make -f makefile.wave_generator

tb: clean
	make -f makefile.tb

clean:
	rm -r -f sim_build
	rm -f results.xml
