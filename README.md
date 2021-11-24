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
The following tools are used for the IO processes shown below. 
- Inkex
- recurrink\_input.py
- recurrink\_effect.py
- recurrink\_cli.py
- Text editor
These may be run in either a UI (e.g. Inkscape) or CLI context, or both.

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
|CSV + JSON | recurrink\_cli | RINK config|

### UC5 Create a new configuration using CLI
Although there are no hard inputs you can clone existing sources to use as a starting point.

| Tool | Output |
| ---  | --- |
|Text editor | CSV + JSON|

### UC6 Automate new models from existing config
This is another way to do UC3 but at the command-line instead of the Inkscape UI.

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
The scores range from 8 (2 x 2 x 2 simplest) to 3,744 (12 x 12 x 26 is the most complex done so far).

| Input | Tool | Output |
| ---   | ---  | --- |
|RINK config | recurrink\_cli | model metadata|
