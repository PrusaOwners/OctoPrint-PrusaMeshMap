/*
 * View model for OctoPrint-PrusaMeshMap
 *
 * Author: Jake Skipper
 * License: MIT
 */
$(function() {
    function PrusameshmapViewModel(parameters) {
        var self = this;

        // assign the injected parameters, e.g.:
        self.loginStateViewModel = parameters[0];
        self.settingsViewModel = parameters[1];
        self.controlViewModel = parameters[2];

	// Assign matplotlib color dropdown options
	self.matplotlib_heatmap_theme_options = ["viridis", "plasma", "inferno", "magma"];
    self.matplotlib_heatmap_background_image_style = ["MK52 Mode", "Generic Klipper Mode"];
    self.output_mode - ["Bicubic Interpolation", "ContourF Topology Map"];

        // TODO: Implement your plugin's view model here.
        self.sendPrusaBedLevel = function() {
            levelGcode = self.settingsViewModel.settings.plugins.PrusaMeshMap.do_level_gcode()
            OctoPrint.control.sendGcode(levelGcode.split("\n"));
        };

    }

    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: PrusameshmapViewModel,
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: [ "loginStateViewModel", "settingsViewModel", "controlViewModel" ],
        // Elements to bind to, e.g. #settings_plugin_PrusaMeshMap, #tab_plugin_PrusaMeshMap, ...
        elements: [ "#settings_plugin_PrusaMeshMap", "#tab_plugin_PrusaMeshMap" ]
    });
});
