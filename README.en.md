[![en](https://img.shields.io/badge/lang-en-blue.svg)](https://github.com/Randroidev/PandoRa/blob/master/README.en.md)
[![ru](https://img.shields.io/badge/lang-ru-red.svg)](https://github.com/Randroidev/PandoRa/blob/master/README.md)

# PandoRa
**Data Visualization App**
PandoRa is a data visualization tool designed for analyzing battery parameters and other time-series data. It supports numerical, percentage, and boolean data (state/process flags), automatically synchronizes plots, and allows flexible column selection. An application for visualizing numerical, percentage, and boolean data with shared timestamps.

For example:

|                     | Voltage | Current | WEAR % | FD    | FC    | RCA   | F-CH | F-DCH |
|---------------------|---------|---------|--------|-------|-------|-------|------|-------|
| 2025-01-23 10:00:00 | 9000    | 3000    | 0      | TRUE  | FALSE | TRUE  | 1    | 0     |
| 2025-01-23 11:00:00 | 10350   | 2025    | 10     | FALSE | FALSE | FALSE | 1    | 0     |
| 2025-01-23 11:00:00 | 12600   | 0       | 30     | FALSE | TRUE  | FALSE | 0    | 0     |
| 2025-01-23 12:00:00 | 18070   | -1750   | 100    | FALSE | FALSE | FALSE | 0    | 1     |
| 2025-01-23 13:00:00 | 9000    | 0       | 90     | TRUE  | FALSE | TRUE  | 0    | 0     |

This table contains a mixed dataset - numerical parameters, percentage values, state flags, and process flags.
Such data can be visualized on a single chart with synchronized scaling and scrolling for convenient analysis using the **PandoRa** application.
![](https://github.com/Randroidev/PandoRa/blob/master/images/_DemoGenBatt.png)

## Data Types
### Timestamp
The timestamp is stored in the first column.
### Numeric
Numerical data is displayed on the main chart with the left scale.
### Percent
Percentage data is displayed on the main chart with the right scale.
The column name for percentage data must contain the percent sign `%`.
### State Flag
State flags are displayed as flags at the top of the canvas.
The data format for state flags is `BOOLEAN`.
### Process Flag
Process flags are displayed as background shading on the main chart.
Process flag column names must start with `F-`.

Other data types are treated as numerical and will be displayed as charts.

## Data Parser
The parser is based on [Pandas](https://pandas.pydata.org/about/index.html) and supports the following file types:
- `.xls` (Excel 97-2003)
- `.xlsx` (Excel 2007 and later)
- `.xlsm` (Excel 2007 and later with macros)
- `.xlsb` (Excel 2007 and later in binary format)
- `.odf` (OpenDocument Format)
- `.ods` (OpenDocument Spreadsheet)

## Command Line
When starting, PandoRa expects a filename in the command line. 
If no file is specified in the command line arguments or if it's inaccessible, the program attempts to open a file named `data.xls` in the current directory. 
If the file doesn't exist, the program displays a dialog box for file selection.

## Demo Data Generation
Demo data generation is available using the following keys:
-    `--demo 300 6` - generates 300 points with 8 random signals
-    `--demo batt` - generates a dataset of three charge-discharge cycles of a battery with a polling frequency of every 10 seconds, resulting in 11881 points over 33 hours.
During demo generation, the program creates a temporary file `pandora_demo.xlsx` in the current directory for demonstration purposes.
![](https://github.com/Randroidev/PandoRa/blob/master/images/_DemoGenRand.png)

## Features and GUI
The application is written in Python using [tkinter](https://docs.python.org/3/library/tkinter.html) and [matplotlib](https://matplotlib.org/).
The application interface may lag during chart rendering, especially with large datasets. 
The dark theme interface tends to lag more noticeably than the light theme.
Scaling and scrolling are performed with mouse buttons held down.

### Column Selection for Display
The application provides the ability to select columns for display. 
To do this, simply check the corresponding checkbox in the `Column Settings` window, which is called by the button with a checkmark.
The application automatically suggests excluding columns whose values remain unchanged throughout the dataset.
![](https://github.com/Randroidev/PandoRa/blob/master/images/_ColumnSelector.png)

### G
This button toggles the background in state flag charts.

### T
This button toggles the display of time labels corresponding to points in the dataset.
On large datasets, this may significantly slow down performance and hinder visual perception.

### Theme
The application has dark and light themes.

### Scaling by State Flags
Clicking on a state flag chart will scale the charts to the boundaries of the area where the click was made.

## Settings
The application has flexible settings that can be modified in the `settings.ini` file or in the GUI. 
Settings marked with `[*]` are properly applied after restarting the application.
If the configuration file is missing, the program creates a new one with default parameters.
![](https://github.com/Randroidev/PandoRa/blob/master/images/_Settings.png)

## Interaction with KNN
[Interaction with KNN](https://github.com/Randroidev/PandoRa/blob/master/KNN.md)