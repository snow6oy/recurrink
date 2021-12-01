# recurrink
An inkscape extension to create recurring patterns

## Introduction to Recurrink
Blocks, Cells and Models make a recurrink.

![block cell model](./tutorial/classBlockModel.svg)

- A model is a template made from repeating blocks
- A block is a collection of cells, marked by the red box above
- A cell is the smallest unit as shown in blue

A recurrink is the final outcome. A model styled to create a digital pattern in SVG format.

![soleares](./tutorial/soleares.svg)

_source file [soleares.svg](./samples/soleares.svg)_

## Inputs, Outputs and Tools

### Inputs
The following file types are used to produce a recurrink.

#### block CSV
The positon for each cell in the block is defined in the CSV file. 
```
a b a
c d c
```
_source file [soleares.csv](models/soleares.csv)_
#### cell JSON 
Each cell also has a shape and style defined using JSON. 
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
_source file [soleares.json](models/soleares.json)_.
#### rink JSON
The recurrink configuration file (JSON) combines information from both the first and second files. It is a build file used to simplify creation of the model SVG.

#### SVG model
The model created from the RINK config lays out the design in neutral colours. Once opened, a RINK file must be manually saved using the `.svg` file extension. Once that is done, then we can get creative :gift:.

### Outputs
From these inputs the following output files can be generated
- rink JSON 
- model SVG
- recurrink SVG

### Tools
The processing is mostly done using these tools.

- Inkscape
- Recurrink Input
- Recurrink Effect
- Recurrink CLI

A text editor is needed to create the `block.csv` and `cells.json` files. 

![life cycle](./tutorial/lifeCycle.svg)


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
