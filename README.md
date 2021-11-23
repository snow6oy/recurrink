# recurrink
Inkscape extension to create recurring patterns

## Introduction to Recurrink
Blocks, Cells and Models make a recurrence.
A recurrence is the final outcome. A digital pattern in SVG format.

## Inputs and Outputs and Tools

### Inputs
- CSV block
- JSON styles
- RINK config (JSON) 
- SVG model 

### Outputs
- RINK config (JSON) 
- SVG model 
- SVG recurrence

### Tools
- Text editor
- Inkscape
- recurrink\_input.py
- recurrink\_effect.py
- CLI

## Use cases and process
### UC1 Get to know recurrink by example

SVG model -> Inkscape -> SVG recurrence

### UC2 Update shapes in a model

| Input | Tool | Output |
| ---   | ---  | --- |
| SVG model | Inkscape + effect | SVG recurrence|

### UC3 Create a new model from existing config

RINK config -> Inkscape + input -> SVG model

### UC4 Create a RINK config from existing sources

CSV + JSON -> configure.py -> RINK config

### UC5 Create a new configuration using CLI

Text editor -> CSV + JSON

### UC6 Automate new models from existing config
(same outcome as UC6 but with CLI)

RINK config -> CLI + input -> SVG model

### UC8 Automated building of SVG recurrences
(same outcome as UC2 but with CLI. Not common use-case but useful for testing)

SVG model -> CLI + effect -> SVG recurrence

### UC9 Choose model by using a complexity index
complexity == rows x cols x uniqCells

RINK config -> configure.py -> model metadata
