# coding=utf-8
from __future__ import absolute_import

### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin, settings and asset plugin. Feel free to add or remove mixins
# as necessary.
#
# Take a look at the documentation on what other plugin mixins are available.

import datetime
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import re
import octoprint.plugin
import octoprint.printer

class PrusameshmapPlugin(octoprint.plugin.SettingsPlugin,
                         octoprint.plugin.AssetPlugin,
                         octoprint.plugin.TemplatePlugin,
                         octoprint.plugin.StartupPlugin,
                         octoprint.plugin.EventHandlerPlugin):

	##~~ SettingsPlugin mixin

	def get_settings_defaults(self):
		return dict(
                        do_level_gcode= 'G28 W ; home all without mesh bed level\nG80 ; mesh bed leveling\nG81 ; check mesh leveling results'
		)

	##~~ AssetPlugin mixin

	def get_assets(self):
		# Define your plugin's asset files to automatically include in the
		# core UI here.
		return dict(
			js=["js/PrusaMeshMap.js"],
			css=["css/PrusaMeshMap.css"],
			less=["less/PrusaMeshMap.less"],
                        img_heatmap=["img/heatmap.png"]
		)
                
	##~~ TemplatePlugin mixin

        #def get_template_configs(self):
        #        return [
        #                dict(type="navbar", custom_bindings=False),
        #                dict(type="settings", custom_bindings=False)
        #        ]
        
        ##~~ EventHandlerPlugin mixin

        def on_event(self, event, payload):
            if event is "Connected":
                self._printer.commands("M1234")

	##~~ Softwareupdate hook

	def get_update_information(self):
		# Define the configuration for your plugin to use with the Software Update
		# Plugin here. See https://github.com/foosel/OctoPrint/wiki/Plugin:-Software-Update
		# for details.
		return dict(
			PrusaMeshMap=dict(
				displayName="Prusameshmap Plugin",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="ff8jake",
				repo="OctoPrint-PrusaMeshMap",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/ff8jake/OctoPrint-PrusaMeshMap/archive/{target_version}.zip"
			)
		)

        ##~~ GCode Received hook

        def mesh_level_check(self, comm, line, *args, **kwargs):
                if re.match(r"^(  -?\d+.\d+)+$", line):
                    self.mesh_level_responses.append(line)
                    self.mesh_level_generate()
                    self._logger.info("FOUND: " + line)
                    return line
                else:
                    return line

        ##~~ Mesh Bed Level Heatmap Generation

        mesh_level_responses = []

        def mesh_level_generate(self):
            if len(self.mesh_level_responses) == 7:

                processed_responses = []

                for response in self.mesh_level_responses:
                    response = re.sub(r"^[ ]+", "", response)
                    response = re.sub(r"[ ]+", ",", response)
                    processed_responses.append([float(i) for i in response.split(",")])

                self._logger.info(str(processed_responses));

                # Let's take our list of lists and make it into
                # a numpy array that matplotlib can do something
                # with. We'll also take this opportunity to
                # reverse the order (Y Axis). Of course, this will
                # make things upside down for the user. So, we'll
                # flip it again before rendering the heatmap image.
                # This lets us get 0,0 at the bottom left corner.
                float_array = np.array(list(reversed(processed_responses)))

                # Set figure and gca objects, this will let us
                # adjust things about our heatmap image as well
                # as adjust axes label locations.
                fig = plt.figure()
                ax = plt.gca()

                # Calculate our heatmap. Interpolation is used
                # to create the smooth looks. At this point you
                # can still adjust some visual elements later.
                # "cmap" controls the matplotlib colormap scheme.
                plt.imshow(float_array, interpolation='spline16', cmap='plasma')

                # Set various options about the graph image before
                # we generate it. Things like labeling the axes and
                # colorbar, and setting the X axis label/ticks to
                # the top to better match the G81 output.
                plt.title("Mesh Level: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                plt.xlabel("X Axis")
                plt.ylabel("Y Axis")
                plt.colorbar(label="Bed Variance (in mm)")

                # Flip that Y Axis again to put 0 at the bottom.
                # Since we inverted our Y Axis above as well, this
                # will also correct the view on the final heatmap.
                ax.invert_yaxis()

                # Save our graph as an image in the current directory.
                self._logger.info("Mesh heatmap saved to " + self.get_asset_folder() + "/img/heatmap.png")
                fig.savefig(self.get_asset_folder() + '/img/heatmap.png')


                del self.mesh_level_responses[:]

# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Prusa Mesh Leveling"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = PrusameshmapPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
                "octoprint.comm.protocol.gcode.received": __plugin_implementation__.mesh_level_check
	}

