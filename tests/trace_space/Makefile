default: input

input: clean
	gmsh -3 src/basin.geo > gmsh.log 2> gmsh_err.log -o basin.msh

clean:
	rm -f *.vtu *.s *.stat *.log *.msh
