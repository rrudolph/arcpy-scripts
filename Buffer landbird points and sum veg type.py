
# Name: Buffer landbird points and sum veg type.py
# Description: Summarize the vegetation by area within 125 meters of landbird points.  Taken from ESRI python example for arcpy.Statistics_anaysis. Adapted for Channel Islands National Park
# landbird program.  Can be used for multiple islands as long as the projections are the same for input fields.
#
# Author: R. Rudolph, National Park Service
# email: rocky_rudolph@nps.gov
# Date: 3/2/15

# Import system modules
import arcpy
from arcpy import env
 
# Set environment settings.
env.workspace = r"C:\Temp\Python Demo\05_LandBirdAnalisys\scratch.gdb"
env.overwriteOutput = True
 
# Set local variables
# Input
inPoints = r"C:\Temp\Python Demo\05_LandBirdAnalisys\scratch.gdb\SBI_LB_points" # Points to be analyzed
inVegetation = r"H:\Shared\Projects\SBI\SBI Veg Map\SBI_veg_2010.mdb\SBI_VegMap_2010" # Veg map.  Make sure it's the same projection.

# Output
outputXLSfolder = r"C:\Temp\Python Demo\05_LandBirdAnalisys\xls\\" 
outStatsTable = r"C:\GIS\Projects\linda\Veg analysis Aug 2014\scratch.gdb\\" + name + "_stats" # Use this to change where the tables go if needed. 


caseField = "alliance_draft1" # Field to perform stats on.  In this case, it's the name of veg alliance.
bufferDistance = "125 METERS"
dissolveType = "LIST"
dissolveField = "ident" 
sideType = "FULL"
endType = "ROUND"
statsFields = [["Shape_Area", "SUM"]]

try:
	# Start looping through each point in the landbird point file specified above.
 	with arcpy.da.SearchCursor(inPoints, ["ident"]) as cursor:
		for row in cursor:
			name = row[0] # Name of the point.  Make sure to change "ident" above to whatever field you need.
			print "------------------------------------"
			print "Processing landbird point: " + name
			print "------------------------------------"

			# Select an individual point from the list of points
			print "Selecting point..."
			arcpy.Select_analysis(inPoints, name, '"ident" = \'' + name + '\'')

			# Execute Buffer to get a buffer of selected point
			print "Buffering point..."
			arcpy.Buffer_analysis(name, name + "_buff", bufferDistance, sideType, endType, dissolveType, dissolveField)
			 
			# Execute Clip using the buffer output to get a clipped feature class
			#  of vegetation
			print "Clipping buffered point..."
			arcpy.Clip_analysis(inVegetation, name + "_buff", name + "_clip")
			 
			# Execute Statistics to get the area of each vegetation type within
			#  the clipped buffer.
			print "Generating area statistics for the buffered and clipped point..."
			arcpy.Statistics_analysis(name + "_clip", outStatsTable, statsFields, caseField)

			# Add a Percent field to the output stats table
			print "Adding percent field..."
			arcpy.AddField_management(outStatsTable, "Percent", "DOUBLE", 9, "#", "#", "#", "#", "#")

			# Sum all the area of the buffer. It's generally going to be about 49087 square meters, but could get clipped to be smaller it it should be caculated each time. 
			print "Sum up the area..."
			summed_total = 0
			with arcpy.da.SearchCursor(outStatsTable, ["SUM_Shape_Area"]) as cursor2:
				for row2 in cursor2:
					summed_total = summed_total + row2[0]

			# Calculate the percent for each record in the buffered point. 
			# This is to visually inspect the data to find out what veg is dominant.
			print "Calculating percentage of vegetation for each buffered area..."
			# Update cursor is for writing individual records to a featureclass
			upcursor = arcpy.da.UpdateCursor(outStatsTable,["Percent", "SUM_Shape_Area"])
			for row3 in upcursor:
				# Calculate each percent by (area of veg type)/(total area). Times this by 100 to get percent. Round to two decimal places. 
				row3[0] = round((row3[1] / summed_total) * 100, 2)
				upcursor.updateRow(row3)

			# Export the table to an excel spreadsheet. This makes it easier for non-GIS people to view.
			print "Exporting table to excel..." 
			arcpy.TableToExcel_conversion(outStatsTable, outputXLSfolder + name + ".xls")

			print "Done with " + name + ". Moving on to next point..."

	print "Script completed.  Have a nice day."

except Exception as e:
    # If an error occurred, print line number and error message
    import traceback
    import sys
    tb = sys.exc_info()[2]
    print "Line {0}".format(tb.tb_lineno)
    print e.message