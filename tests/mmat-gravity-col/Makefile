input: clean
	gmsh -3 src/mmat-gravity-col.geo
	../../scripts/gmsh2triangle src/mmat-gravity-col.msh

clean:
	rm -rf *.d.* *.stat *.vtu *.convergence mmat-gravity-col.node mmat-gravity-col.face mmat-gravity-col.ele src/set_phi *checkpoint*
