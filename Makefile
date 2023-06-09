SCAL := $(shell ./mondrian -f)
m := $(shell ./mondrian -n)
AUTH := machine
# examples: m=afroclave OR m=soleares ID=66862c76787f3994f64cb79882d246f
BASEDIR := /home/gavin/Pictures/artWork/recurrences

help :
	@echo "make csv 				randomly generate new CSV in tmp"
	@echo "make csv 	m=waltz AUTH=human	as above with default values"
	@echo "make svg 	m=waltz		build SVG from tmp CSV"
	@echo "make svg 	m=waltz AUTH=human	as above but JSON recorded in db with human author"
	@echo "make view 	m=waltz           	copy values from CSV to SVG with forced rebuild of SVG"
	@echo "make install 	m=waltz 		mv JSON and SVG to database and put entry in pub queue"
	@echo "make clean 	m=<model>		remove CSV, JSON, RINK, SVG, PID from previous build"
# testing
hi : 
	@echo "$@ $(USER) with $(m) by $(AUTH) at $(SCAL)"
clean :
	rm /tmp/$(m).*
	rm /tmp/$(m)_*
	rm /tmp/rink.pid

csv : $(BASEDIR)/$(m)/index.csv
	./mondrian -c -m $(m) -a $(AUTH)
# we do not make index.csv but declare it as a dependency because if there is none then make will STOP
$(BASEDIR)/$(m)/index.csv :
	@echo $@

# SVG used as input and output for cell updates
# TODO can we pickup MODL using /tmp/*.csv 
svg: /tmp/$(m).svg
	@echo $@
/tmp/$(m).svg : /tmp/$(m).rink
	@echo $@ 
	./input.py --output $@ --scale $(SCAL) /tmp/$(m).rink
# RINK needed to build initial SVG
/tmp/$(m).rink : /tmp/rink.pid
	@echo $@
	./mondrian -s -m $(m)
/tmp/rink.pid : 
	@echo $@
	./mondrian -j -m $(m) -a $(AUTH)
# declaring target 'csv' as a dependency will overwrite
/tmp/$(m).csv : 
	ls $@

# update SVG from CSV
# view : /tmp/$(MODL).csv /tmp/$(MODL).svg
view : /tmp/rink.pid
	./mondrian -u -m $(m)
	@echo $@

install : /tmp/rink.pid
	./mondrian -i

repair:
	./mondrian.py -m $(m) --output RINK --view $(VIEW)
	./input.py --output $(BASEDIR)/$(m)/$(VIEW).svg --scale $(SCAL) /tmp/$(m).rink
