# Changelog

## v0.3.1

** Added display of what adjustments need to be made to graph

## v0.2.1

**Bug Fixes:**
* Forgot to update version number in setup.py. This was causing OctoPrint to continuously alert that there was a plugin update when there wasn't.

## v0.2.0

**New Features:**
* Added a drop down in plugin settings to select matplotlib colormap to use on the heatmap image.
* Default colormap set to **viridis** to better align with OctoPrint's color scheme.
* Added bed variance total to colorbar label.

## v0.1.2

**Bug Fixes:**
* Added a matplotlib >= 2.2.0 version check as some people had an older version of matplotlib installed that was too old.
* Declared dependency packages as some users are running pip installs that don't automatically fetch them when installing matplotlib/numpy.
Thanks **koenkooi** for those fixes.

## v0.1.1

**Bug Fixes:**
* Fixed an incorrect URL in the HTML template.

## v0.1.0

**Initial Release**
