# OctoPrint-PrusaMeshMap

## This plugin is undergoing alpha testing! ##

## Description

This OctoPrint plugin will create a "Prusa Mesh Leveling" tab with controls to initiate a mesh bed level operation. By default the GCode script it runs (configurable in settings!) will also do a G81 mesh level status check. This plugin has a hook defined that watches for the Prusa mesh level status lines and every time it receives a full seven line group of them, it will process a new heatmap viewable on the tab. Going the hook route has the advantage in that you can add G81 to your slicer start GCode and get a new heatmap every print, just click the "reload" button below the heatmap image to see it.

## Setup

Install via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager)
or manually using this URL:

    https://github.com/ff8jake/OctoPrint-PrusaMeshMap/archive/master.zip
