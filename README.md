# Arduino Data Acquisition

## _Data Acquisition Software based in Arduino_
![](https://img.shields.io/badge/Arduino-informational?style=flat&logo=arduino&logoColor=white&color=#00979D)
[](https://img.shields.io/badge/Code-Python-informational?style=flat&logo=python&logoColor=white&color=blue)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)

This software was developed as part of my Masters in Mechanical Engineering project. I was in need of a reliable way of measuring temperature in different points.

The hardware allows for 5 different data points, collected by 5 MAX6675 Digital Converters.

![Arduino DAQ](tela_software.png "Data Acquisition using Python and Arduino")

## Objectives

Development of a simple UI tha allows reading the temperature on the fly and generate a CSV file with all data:

* Development of a Python based UI using wxPython module
* Allow for real time tracking of data
* Allow for generation of CSV report

## Dependencies

matplotlib, pyserial and wxPython

```sh
pip install -U matplotlib pyserial wxPython
```
