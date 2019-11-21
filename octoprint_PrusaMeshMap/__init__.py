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
import matplotlib.image as mpimg
import re
import octoprint.plugin
import octoprint.printer
import json



class PrusameshmapPlugin(octoprint.plugin.SettingsPlugin,
                         octoprint.plugin.AssetPlugin,
                         octoprint.plugin.TemplatePlugin,
                         octoprint.plugin.StartupPlugin,
                         octoprint.plugin.EventHandlerPlugin):

    ##~~ SettingsPlugin mixin



    def get_settings_defaults(self):
        return dict(
            do_level_gcode = 'bed_mesh_map',
            matplotlib_heatmap_theme = 'viridis',
            matplotlib_heatmap_background_image_style = 'MK52 Mode',
            output_mode = 'ContourF Topology Map',
            pluginTestingMode = 'False'
        )
    def get_current_settings(self):
        return dict(
            do_level_gcode=self._settings.get(["do_level_gcode"]),
            matplotlib_heatmap_theme = self._settings.get(["matplotlib_heatmap_theme"]),
            matplotlib_heatmap_background_image_style = self._settings.get(["matplotlib_heatmap_background_image_style"]),
            output_mode = self._settings.get(["output_mode"]),
            pluginTestingMode = self._settings.get(["pluginTestingMode"])
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
            #self._printer.commands("M1234")
                pass
    ##~~ Softwareupdate hook

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://github.com/foosel/OctoPrint/wiki/Plugin:-Software-Update
        # for details.
        return dict(
            PrusaMeshMap=dict(
                displayName="PrusaKlippermeshmap Plugin",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="ff8jake,mcm001",
                repo="OctoPrint-PrusaMeshMap",
                current=self._plugin_version,

                # update method: pip
                pip="https://github.com/mcm001/OctoPrint-PrusaMeshMap/archive/{target_version}.zip"
            )
        )

        ##~~ GCode Received hook


    def mesh_level_check(self, comm, line, *args, **kwargs):
        #self._logger.info("Searching line..." + line)
        if re.match(r"^(  -?\d+.\d+)+$", line):
            self.mesh_level_responses.append(line)
            self._logger.info("FOUND: " + line)
            self.mesh_level_generate()
            return line
        elif line.startswith("mesh_map_output"):
            self._logger.info("Klipper bed data found. Forwarding to the processor: " + line)
            klipper_json_line = line
            self.generate_graph_klipper_mode(klipper_json_line)
            return line
        elif (self.get_current_settings()["pluginTestingMode"] == 'True') and (line.startswith('ok')):
            self._logger.info("Processing in Testing mode")
            klipper_json_line = line
            self.generate_graph_klipper_mode(klipper_json_line)
        else:
            return line


        # Klipper mode heatmap generation. Above brig's stuff because it's better :D

    def generate_graph_klipper_mode(self,klipper_json_line):

        self._logger.info("Processing in Klipper mode...")
        #Remove the first 16 charicters of the line and import to a dictionary
        #use this line for testing
        if self.get_current_settings()["pluginTestingMode"] == 'True':
            klipper_json_line = 'mesh_map_output {"max_point": [212.0, 204.0], "z_positions": [[-0.12499999999999833, -0.10999999999999777, -0.09750000000000203, -0.1399999999999989, -0.2200000000000043], [0.014999999999995128, 0.02749999999999797, 0.012499999999997402, -0.016249999999997766, -0.0500000000000026], [0.02749999999999797, 0.03250000000000053, 0.02875000000000394, 0.046250000000002234, 0.034999999999998255], [0.04000000000000081, 0.07750000000000223, 0.07999999999999996, 0.0787500000000011, 0.08124999999999882], [-0.01000000000000345, 0.05249999999999655, 0.11750000000000138, 0.11750000000000138, 0.10250000000000081]], "xy_offset": [24.0, 5.0], "min_point": [2.0, 0.0]}'
        klipper_json_line = klipper_json_line[16:]
        jsonDict = json.loads(klipper_json_line)
        xyOffset = jsonDict["xy_offset"]
        minPoints = jsonDict["min_point"]

        #Set up minimum and max points, arrays, math, etc
        minPoints[0]=minPoints[0]+xyOffset[0]
        minPoints[1]=minPoints[1]+xyOffset[1]
        maxPoints = (jsonDict["max_point"])
        maxPoints[0] = maxPoints[0]+xyOffset[0]
        maxPoints[1] = maxPoints[1]+xyOffset[1]
        z_positions = np.array(jsonDict["z_positions"])
        z_positions_shape = z_positions.shape
        minMax = [minPoints[0],maxPoints[0],minPoints[1],maxPoints[1]]
        #probeSpacingX = (maxPoints[0]-minPoints[0])/(z_positions_shape[1]-1)
        #probeSpacingY = (maxPoints[1]-minPoints[1])/(z_positions_shape[0]-1)

        #Variables shamelessly reused from the stock FW code
        BED_SIZE_X = 250
        BED_SIZE_Y = 210
        #BED_PRINT_ZERO_REF_X = 2
        #BED_PRINT_ZERO_REF_Y = 9.4
        SHEET_OFFS_X = 0
        SHEET_OFFS_Y = 0
        SHEET_MARGIN_LEFT = 0
        SHEET_MARGIN_RIGHT = 0
        SHEET_MARGIN_FRONT = 17
        SHEET_MARGIN_BACK = 14
        sheet_left_x = -(SHEET_MARGIN_LEFT + SHEET_OFFS_X)
        sheet_right_x = sheet_left_x + BED_SIZE_X + SHEET_MARGIN_LEFT + SHEET_MARGIN_RIGHT
        sheet_front_y = -(SHEET_MARGIN_FRONT + SHEET_OFFS_Y)
        sheet_back_y = sheet_front_y + BED_SIZE_Y + SHEET_MARGIN_FRONT + SHEET_MARGIN_BACK

        #Define probe points to plot and meshgridify them
        xProbePoints=np.linspace(minPoints[0],maxPoints[0],z_positions_shape[1],endpoint=True)
        yProbePoints=np.linspace(minPoints[1],maxPoints[1],z_positions_shape[0],endpoint=True)
        xProbePoints, yProbePoints = np.meshgrid(xProbePoints,yProbePoints)

        #Plot all of the things, including the mk52 back
        plt.gcf().clear()

        #Put the date at the top
        plt.title("Mesh Level: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        if self.get_current_settings()["matplotlib_heatmap_background_image_style"] == "MK52 Mode":
            img = mpimg.imread(self.get_asset_folder() + '/img/mk52_steel_sheet.png')
        #else use a different image, uhh not sure what yet

        #Plot whichever image is selected per the above if/else
        plt.imshow(img, extent=[sheet_left_x, sheet_right_x, sheet_front_y, sheet_back_y], interpolation="lanczos", cmap=plt.cm.get_cmap('viridis'))
        

        #plot the interpolated mesh, bar, and probed points
        #Depending on which mode you set it to
        if self.get_current_settings()["output_mode"] == "Bicubic Interpolation":
            image = plt.imshow(np.flip(z_positions,axis=0),interpolation='bicubic',cmap='viridis',extent=minMax)#Plot the background 
            plt.colorbar(image,label="Measured Level (mm)")#Color bar on the side
        if self.get_current_settings()["output_mode"] == "ContourF Topology Map":
            contour = plt.contourf(xProbePoints, yProbePoints, z_positions, alpha=.75, antialiased=True, cmap=plt.cm.get_cmap(self._settings.get(["matplotlib_heatmap_theme"])))
            plt.colorbar(contour, label="Measured Level (mm)")
            #If you need to invert the data, use [::-1]
        
        plt.scatter(xProbePoints,yProbePoints,color='r')#Scatterplot of probed points

        if self.get_current_settings()["matplotlib_heatmap_background_image_style"] == "MK52 Mode":
            #Plot the standoffs
            standoff_min = [15,0]
            standoff_max = [235,210]
            standoff_count = [3,3]
            standoff_X = np.linspace(standoff_min[0],standoff_max[0],standoff_count[0],endpoint=True)
            standoff_Y = np.linspace(standoff_min[1],standoff_max[1],standoff_count[1],endpoint=True)
            standoff_X, standoff_Y = np.meshgrid(standoff_X,standoff_Y)
            plt.scatter(standoff_X,standoff_Y,color='tab:orange')

        #Add fancy titles
        plt.xlabel("X Axis (mm)")
        plt.ylabel("Y Axis (mm)")


        #Plot with fancy contourf


        

        # Save our graph as an image in the current directory.
        
        plt.savefig(self.get_asset_folder() + '/img/heatmap.png', bbox_inches="tight")
        #plt.savefig('/home/pi/heatmap.png', bbox_inches="tight")
        



        
        plt.gcf().clear()
        plt.tight_layout()
        self._logger.info("Heatmap updated in Klipper Mode")


    ##~~ Mesh Bed Level Heatmap Generation
    ##~~Stock firmware style

    mesh_level_responses = []

    def mesh_level_generate(self):

            # We work with coordinates relative to the dashed line on the
            # skilkscreen on the MK52 heatbed: print area coordinates. Note
            # this doesn't exactly line up with the steel sheet, so we have to
            # adjust for that when generating the background image, below.
            # Points are measured from the middle of the PINDA / middle of the
            # 4 probe circles on the MK52.

        MESH_NUM_POINTS_X = 7
        MESH_NUM_MEASURED_POINTS_X = 3
        MESH_NUM_POINTS_Y = 7
        MESH_NUM_MEASURED_POINTS_Y = 3
        BED_SIZE_X = 250
        BED_SIZE_Y = 210

            # These values come from mesh_bed_calibration.cpp
        BED_PRINT_ZERO_REF_X = 2
        BED_PRINT_ZERO_REF_Y = 9.4

            # Mesh probe points, in print area coordinates
            # We assume points are symmetrical (i.e a rectangular grid)
        MESH_FRONT_LEFT_X = 37 - BED_PRINT_ZERO_REF_X
        MESH_FRONT_LEFT_Y = 18.4 - BED_PRINT_ZERO_REF_Y

        MESH_REAR_RIGHT_X = 245 - BED_PRINT_ZERO_REF_X
        MESH_REAR_RIGHT_Y = 210.4 - BED_PRINT_ZERO_REF_Y

            # Offset of the marked print area on the steel sheet relative to
            # the marked print area on the MK52. The steel sheet has margins
            # outside of the print area, so we need to account for that too.

        SHEET_OFFS_X = 0
            # Technically SHEET_OFFS_Y is -2 (sheet is BELOW (frontward to) that on the MK52)
            # However, we want to show the user a view that looks lined up with the MK52, so we
            # ignore this and set the value to zero.
        SHEET_OFFS_Y = 0
                               #
        SHEET_MARGIN_LEFT = 0
        SHEET_MARGIN_RIGHT = 0
            # The SVG of the steel sheet (up on Github) is not symmetric as the actual one is
        SHEET_MARGIN_FRONT = 17
        SHEET_MARGIN_BACK = 14

        sheet_left_x = -(SHEET_MARGIN_LEFT + SHEET_OFFS_X)
        sheet_right_x = sheet_left_x + BED_SIZE_X + SHEET_MARGIN_LEFT + SHEET_MARGIN_RIGHT
        sheet_front_y = -(SHEET_MARGIN_FRONT + SHEET_OFFS_Y)
        sheet_back_y = sheet_front_y + BED_SIZE_Y + SHEET_MARGIN_FRONT + SHEET_MARGIN_BACK


        mesh_range_x = MESH_REAR_RIGHT_X - MESH_FRONT_LEFT_X
        mesh_range_y = MESH_REAR_RIGHT_Y - MESH_FRONT_LEFT_Y

        mesh_delta_x = mesh_range_x / (MESH_NUM_POINTS_X - 1)
        mesh_delta_y = mesh_range_y / (MESH_NUM_POINTS_Y - 1)

            # Accumulate response lines until we have all of them
        if len(self.mesh_level_responses) == MESH_NUM_POINTS_Y:
            self._logger.info("Generating heatmap")

            # TODO: Validate each row has MESH_NUM_POINTS_X values
            mesh_values = []

                # Parse response lines into a 2D array of floats in row-major order
            for response in self.mesh_level_responses:
                response = re.sub(r"^[ ]+", "", response)
                response = re.sub(r"[ ]+", ",", response)
                mesh_values.append([float(i) for i in response.split(",")])

                # Generate a 2D array of the Z values in column-major order
            col_i = 0
            mesh_z = np.zeros(shape=(7,7))
            for col in mesh_values:
                row_i = 0
                for val in col:
                    mesh_z[col_i][row_i] = val
                    row_i = row_i + 1
                col_i = col_i + 1

                # Calculate the X and Y values of the mesh bed points, in print area coordinates
            mesh_x = np.zeros(MESH_NUM_POINTS_X)
            for i in range(0, MESH_NUM_POINTS_X):
                mesh_x[i] = MESH_FRONT_LEFT_X + mesh_delta_x*i

            mesh_y = np.zeros(MESH_NUM_POINTS_Y)
            for i in range(0, MESH_NUM_POINTS_Y):
                mesh_y[i] = MESH_FRONT_LEFT_Y + mesh_delta_y*i

            bed_variance = round(mesh_z.max() - mesh_z.min(), 3)

                ############
                # Draw the heatmap
                #fig = plt.figure(dpi=96, figsize=(12, 9))
            fig = plt.figure(dpi=96, figsize=(10,8.3))
            ax = plt.gca()

                # Plot all mesh points, including measured ones and the ones
                # that are bogus (calculated). Indicate the actual measured
                # points with a different marker.
            for x_i in range(0, len(mesh_x)):
                for y_i in range(0, len(mesh_y)):
                    if ((x_i % MESH_NUM_MEASURED_POINTS_X) == 0) and ((y_i % MESH_NUM_MEASURED_POINTS_Y) == 0):
                        plt.plot(mesh_x[x_i], mesh_y[y_i], 'o', color='m')
                    else:
                        plt.plot(mesh_x[x_i], mesh_y[y_i], '.', color='k')

                # Draw the contour map. Y values are reversed to account for
                # bottom-up orientation of plot library
            contour = plt.contourf(mesh_x, mesh_y[::-1], mesh_z, alpha=.75, antialiased=True, cmap=plt.cm.get_cmap(self._settings.get(["matplotlib_heatmap_theme"])))

                # Insert the background image (currently an image of the MK3 PEI-coated steel sheet)
            img = mpimg.imread(self.get_asset_folder() + '/img/mk52_steel_sheet.png')
            plt.imshow(img, extent=[sheet_left_x, sheet_right_x, sheet_front_y, sheet_back_y], interpolation="lanczos", cmap=plt.cm.get_cmap(self._settings.get(["matplotlib_heatmap_theme"])))

                # Set axis ranges (although we don't currently show these...)
            ax.set_xlim(left=sheet_left_x, right=sheet_right_x)
            ax.set_ylim(bottom=sheet_front_y, top=sheet_back_y)

                # Set various options about the graph image before
                # we generate it. Things like labeling the axes and
                # colorbar, and setting the X axis label/ticks to
                # the top to better match the G81 output.
            plt.title("Mesh Level: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            plt.axis('image')
                #ax.axes.get_xaxis().set_visible(True)
                #ax.axes.get_yaxis().set_visible(True)
            plt.xlabel("X Axis (mm)")
            plt.ylabel("Y Axis (mm)")

                #plt.colorbar(label="Bed Variance: " + str(round(mesh_z.max() - mesh_z.min(), 3)) + "mm")
            plt.colorbar(contour, label="Measured Level (mm)")

            plt.text(0.5, 0.43, "Total Bed Variance: " + str(bed_variance) + " (mm)", fontsize=10, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, bbox=dict(facecolor='#eeefff', alpha=0.5))

                # Save our graph as an image in the current directory.
            fig.savefig(self.get_asset_folder() + '/img/heatmap.png', bbox_inches="tight")
            self._logger.info("Heatmap updated")

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
