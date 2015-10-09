# dab-flask

This package provides a restful API wrapper around the [keystonepy](https://github.com/vanceb/keystonepy) library, which in turn wraps the c library provided by [Monkeyboard](https://www.monkeyboard.org/) for their [DAB Development board](https://www.monkeyboard.org/products/85-developmentboard/85-dab-dab-fm-digital-radio-development-board-pro).

This also provides a web based UI for the DAB Radio which allows you to change channels, volume, favorite channels, view the text that accompanies the program, and pull out "Now Playing" details from this text to drive a "Playlist".

The aim is to run this in the car controlled by a Raspberry Pi, with control over wifi from a dash-mounted Android tablet.
