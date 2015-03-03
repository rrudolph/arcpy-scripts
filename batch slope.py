# A very simple script that takes all rasters in a directory and performs a slope calculation on them.  It can be adapted to do whatever you want.  
# Note the arcpy.Describe(raster).name variable. This grabs the name of the raster so you can use it later to write a new file with the same name and append text to it to distinguish it from the old file. 
#
# Author: R. Rudolph, National Park Service
# email: rocky_rudolph@nps.gov
# Date: 3/2/15

import arcpy
arcpy.env.workspace = r"C:\Temp\rasters"

arcpy.env.overwriteOutput = False

try:
    arcpy.CheckOutExtension("3D")
    rasters = arcpy.ListRasters()
    for raster in rasters:
        rastername = arcpy.Describe(raster).name
        # output = r"C:\Temp\rasters\rasters.gdb\\" + rastername + "_slope"  #You can also export it out to a file geodatabase. 
        print "Calculating slope for " + rastername
        arcpy.Slope_3d(raster, rastername + "_s") 
    arcpy.CheckInExtension("3D")

except Exception as e:
    # If an error occurred, print line number and error message
    import traceback
    import sys
    tb = sys.exc_info()[2]
    print "Line {0}".format(tb.tb_lineno)
    print e.message
