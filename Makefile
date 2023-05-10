ID := none
SCAL := $(shell ./mondrian -s)
MODL := $(shell ./mondrian -n)
# examples: MODL=afroclave OR MODL=soleares ID=66862c76787f3994f64cb79882d246f
BASEDIR := /home/gavin/Pictures/artWork/recurrences

help :
	@echo "make png 			randomly generate new recurrence"
	@echo "make MODL=<model> ID=<digest>	build SVG from existing recurrence"
	@echo "make clean MODL=<model>		remove CSV, RINK, SVG, PNG from previous build"
# testing
hi : 
	@echo "$@ $(USER) with $(MODL)/$(ID) at $(SCAL)"
clean :
	rm /tmp/$(MODL).*
# we do not make index.csv but declare it as a dependency because if there is none then make will STOP
csv : $(BASEDIR)/$(MODL)/index.csv
	@echo $@
	./recurrink.py -m $(MODL) --output CSV
$(BASEDIR)/$(MODL)/index.csv :
	@echo $@
# generate a JSON in /tmp with a new ID for every CSV file in /tmp
json : *.csv
	@echo $@
*.csv : 
	./builder $(shell ls -1 /tmp/$@)
img: $(MODL).rink
	@echo $@
	./input.py --output /tmp/$(ID).svg $(MODL).rink
# creates a PNG for transfer using mondrian 
# mv /tmp/*.json $(BASEDIR)/$(MODL)/m
rnd : *.svg
	@echo $@
	mv *.svg $(BASEDIR)/$(MODL)/m
	mv *.png /home/gavin/Pictures/pubq
# wildcard resolves to VIEW.svg
# but side-effect is that we have to hide MODEL.svg in /tmp to avoid circular reference
# another side-effect is that unless cleaned there can be many SVGs
*.svg : /tmp/$(MODL).rink
	@echo $@
	/usr/bin/inkscape --export-type=png $@
/tmp/$(MODL).rink : /tmp/$(MODL).csv
	@echo $@ 
	./mondrian -m $(MODL) -r none
# build SVG in tmp, copy VARS to JSON then rename SVG to digest from VARS
# the SVG rename happens in ./mondrian because make threw errors
# removed this dep /tmp/$(MODL).svg
/tmp/$(MODL).csv : 
	@echo $@
	./mondrian -m $(MODL) -d $(ID)
# SVG used as input and output for cell updates
#/tmp/$(MODL).svg :
#	@echo $@ "<- SVG built"
#	./input.py --output $@ --scale $(SCAL) /tmp/$(MODL).rink
# RINK needed to build initial SVG
#$(MODL).rink : 
#	@echo $@
#	./mondrian -m $(MODL) -r $(ID)
#	/usr/bin/mv /tmp/$@ .
