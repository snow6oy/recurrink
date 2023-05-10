SCAL := $(shell ./mondrian -s)
MODL := $(shell ./mondrian -n)
AUTH := machine
# examples: MODL=afroclave OR MODL=soleares ID=66862c76787f3994f64cb79882d246f
BASEDIR := /home/gavin/Pictures/artWork/recurrences

help :
	@echo "make csv 			randomly generate new CSV in tmp"
	@echo "make csv MODL=waltz AUTH=human	as above with default values"
	@echo "make svg MODL=waltz		build SVG from tmp CSV"
	@echo "make svg MODL=waltz AUTH=human	as above but JSON recorded in db with human author"
	@echo "make view MODL=waltz           	copy values from CSV to SVG with forced rebuild of SVG"
	@echo "make install 			mv JSON and SVG to database and put entry in pub queue"
	@echo "make clean MODL=<model>		remove CSV, JSON, RINK, SVG, PID from previous build"
# testing
hi : 
	@echo "$@ $(USER) with $(MODL) by $(AUTH) at $(SCAL)"
clean :
	rm /tmp/$(MODL).*
	rm /tmp/rink.pid

csv : $(BASEDIR)/$(MODL)/index.csv
	./mkcsv $(MODL) $(AUTH)
# we do not make index.csv but declare it as a dependency because if there is none then make will STOP
$(BASEDIR)/$(MODL)/index.csv :
	@echo $@

# SVG used as input and output for cell updates
# TODO can we pickup MODL using /tmp/*.csv 
svg: /tmp/$(MODL).svg
	@echo $@
/tmp/$(MODL).svg : /tmp/$(MODL).rink
	@echo $@ 
	./input.py --output $@ --scale $(SCAL) /tmp/$(MODL).rink
# RINK needed to build initial SVG
/tmp/$(MODL).rink : /tmp/rink.pid
	@echo $@
	./recurrink.py -m $(MODL) --output RINK
/tmp/rink.pid : /tmp/$(MODL).json
	@echo $@
/tmp/$(MODL).json : /tmp/$(MODL).csv
	@echo $@
	./mkjson $(MODL) $(AUTH)
# declaring target 'csv' as a dependency will overwrite
/tmp/$(MODL).csv : 
	ls $@

# update SVG from CSV
view : /tmp/$(MODL).csv /tmp/$(MODL).svg
	./mksvg $(MODL)
	@echo $@

install : /tmp/rink.pid
	./mkinstall
