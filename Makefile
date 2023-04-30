MODL := $(shell ./mondrian -n)
SCAL := $(shell ./mondrian -s)
# example MODL=afroclave
ID := 'none'
# example MODL=soleares ID=66862c76787f3994f64cb79882d246f
PUBDIR := /home/gavin/Pictures/artWork/recurrences/mondrian/

# PNG for transfer from SVG output by cells.sh
png : *.svg
	@echo "made $@"
	mv *.svg /home/gavin/Pictures/pubq
	mv *.png /home/gavin/Pictures/pubq

# wildcard resolves to DIGEST.svg
# but side-effect is that we have to hide MODEL.svg in /tmp to avoid circular reference
# another side-effect is that unless cleaned there can be many SVGs
*.svg : /tmp/$(MODL).csv
	@echo "$@"
	/usr/bin/inkscape --export-type=png $@

# build SVG in tmp, copy VARS to JSON then rename SVG to digest from VARS
# the following SVG rename happens in ./mondrian because it caused race cond.
# /usr/bin/mv /tmp/$(MODL).svg $(shell ./mondrian -m $(MODL) -d).svg
# ./mondrian -m $(MODL)
/tmp/$(MODL).csv : /tmp/$(MODL).svg
	@echo "$@"
	./mondrian -m $(MODL) -d $(ID)

# SVG used as input and output for cell updates
# ./input.py $(MODL).rink > $@
/tmp/$(MODL).svg : $(MODL).rink
	@echo "made $@"
	./input.py --output $@ --scale $(SCAL) $(MODL).rink

# RINK needed to build initial SVG
# TODO update RINK output path in Python
$(MODL).rink : 
	@echo "made $@"
	./mondrian -m $(MODL) -r $(ID)
	/usr/bin/mv models/$@ .

help :
	@echo "make 			randomly generate new recurrence"
	@echo "make svg ID=<digest>	build SVG from existing recurrence"
	@echo "make clean MODL=<model>	remove CSV, RINK, SVG, PNG from previous build"

# testing
hi : 
	@echo "$@ $(USER) with $(MODL)"

clean :
	rm $(MODL).*
	rm /tmp/$(MODL).*
