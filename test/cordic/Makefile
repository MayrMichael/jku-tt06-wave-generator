all: 
	$(MAKE) cordic_slice 
	$(MAKE) cordic_iterative 
	$(MAKE) sin_generator 
	$(MAKE) wave_generator 
	$(MAKE) tb

cordic_slice: clean
	make -f makefile.cordic_slice

cordic_iterative: clean
	make -f makefile.cordic_iterative

sin_generator: clean
	make -f makefile.sin_generator

wave_generator: clean
	make -f makefile.wave_generator

tb: clean
	make -f makefile.tb

clean:
	rm -r -f sim_build
	rm -f results.xml
