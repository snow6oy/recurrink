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

| Input | Tool | Output |
| ---   | ---  | --- |
|SVG model | Inkscape | SVG recurrence|

### UC2 Update shapes in a model

| Input | Tool | Output |
| ---   | ---  | --- |
| SVG model | Inkscape + effect | SVG recurrence|

### UC3 Create a new model from existing config

| Input | Tool | Output |
| ---   | ---  | --- |
|RINK config | Inkscape + input | SVG model|

### UC4 Create a RINK config from existing sources

| Input | Tool | Output |
| ---   | ---  | --- |
|CSV + JSON | configure.py | RINK config|

### UC5 Create a new configuration using CLI
Although there are no hard inputs you can clone existing sources to use as a starting point.

| Tool | Output |
| ---  | --- |
|Text editor | CSV + JSON|

### UC6 Automate new models from existing config
This has the same outcome as UC6 but uses a CLI.

| Input | Tool | Output |
| ---   | ---  | --- |
|RINK config | CLI + input | SVG model|

### UC8 Automated building of SVG recurrences
This has the same outcome as UC2 but using a CLI. Useful for testing during software development.

| Input | Tool | Output |
| ---   | ---  | --- |
|SVG model | CLI + effect | SVG recurrence|

### UC9 Choose model by using a complexity score
A complexity score is calculated using the formula `rows x cols x uniqCells`.
The scores range from 8 (2 x 2 x 2 simplest) to 3,744 (12 x 12 x 26 most complex done so far).

| Input | Tool | Output |
| ---   | ---  | --- |
|RINK config | configure.py | model metadata|
