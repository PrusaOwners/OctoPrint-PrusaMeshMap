# OctoPrint-PrusaMeshMap

## This plugin is undergoing beta testing! ##

## Description

This plugin takes Prusa's G81 mesh level output and translates it into an easy to read heatmap using matplotlib.

Upon installation, you will have a "Prusa Mesh Leveling" tab:

![example showing new tab in interface](example.png)

Clicking "Perform Bed Level and Check" will execute a bed level operation and status check using a GCode script defined in the settings:

![example showing GCode script in settings](example2.png)

It should be noted that the heatmap image **will not** reload automatically. To reload, click "Reload Heatmap Image" below the heatmap. This is to allow you to be paying attention and see how your new bed level result changes.

## G81 Output Handler

It should be noted that this plugin has a handler that is watching output received from the printer **at all times**. This means you can place a G81 in your slicer's GCode start script and have a new heatmap generated every time you print!

## Setup

Install via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager)
or manually using this URL:


    https://github.com/PrusaOwners/OctoPrint-PrusaMeshMap/archive/master.zip

**My modified version can be installed using this URL:**

    https://github.com/AndyQ/OctoPrint-PrusaMeshMap/archive/master.zip


### Raspberry Pi Users

This plugin uses **matplotlib** and **numpy** packages from pip. Since wheels do not exist for these ARM packages in Python 2.7, they will need to compile. This process takes a long time (30min+). If you try to install this directly from Plugin Manager without installing these dependencies first, the compile process will take long enough that OctoPrint errors out the plugin install and quits responding **while the install process continues in the background!** You can monitor the process with **top** command via SSH, and when it finishes attempt the plugin install again per the above. It will detect that the plugin is already installed and force a reinstall, and since the dependencies will be there it will go on without issues.

A better method may be to log in to the Pi via SSH before doing the plugin install and run ``/home/pi/oprint/bin/pip --no-cache-dir install matplotlib numpy`` first (``--no-cache-dir`` for Pi Zero W users, may work fine without this on other Pi versions). This will still take a long time, but will get the packages the plugin depends on in place beforehand. The plugin will then install without issues within a few seconds in Plugin Manager.

