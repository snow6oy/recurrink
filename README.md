# recurrink
An inkscape extension to create recurring patterns

## Introduction to Recurrink
Blocks, Cells and Models make a recurrence.

![block cell model](doc/classBlockModel.svg)

- A model is a template made from repeating blocks
- A block is a collection of cells, marked by the red box above
- A cell is the smallest unit as shown in blue

A recurrence is the final outcome. A model styled to create a digital pattern in SVG format.

## Inputs, Outputs and Tools

### Inputs
The following file types are used to produce a recurrence.

1. SVG model  


#### CSV
The positon for each cell in the block is defined in the CSV file. See [soleares.csv](models/soleares.csv)
```
a b a
c d c
```
#### JSON 
Each model has shape and style defined using JSON. For example [soleares.json](models/soleares.json).
```
{
  "a": {
    "shape": "square",
    "stroke_width": 1
  },
  "b": {
    "shape": "circle",
    "stroke_width": 0
  },
  "c": {
    "shape": "line",
    "stroke_width": 0
  },
  "d": {
    "shape": "triangle",
    "stroke_width": 0
  }
}
```
#### RINK
The recurrink configuration file (JSON) combines information from both the first and second files. It is a build file used to simplify creation of the SVG model.

#### SVG model
The model created from the RINK config lays out the design in neutral colours. The SVG files must be manually saved with an SVG file extension. Once that is done, then we can get creative.

### Outputs
- RINK config (JSON) 
- SVG model 
- SVG recurrence

### Tools
The following tools may be used, depending on which of the use-case shown below apply.

- input.py
- effect.py
- configure.py
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

## Refactor
26/11
     328 configure.py
     259 draw.py
     153 recurrink.py
      97 recurrink_input.py
      66 test.py
     903 total
