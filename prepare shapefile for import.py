#########################################################################
# Script to prepare shapefiles for import into the CHIS InvasiveSpecies
# geodatabase.
#
# inFeatures:  semicolon delimited list of files shapefiles to process.
# outputeFile: name of shapefile to receive the results. If this is a
#              relative path it will be interpreted relative to the first
#              input file.
#
# Created by Parker Abercrombie and Rocky Rudolph at Channel Islands National Park, Ventura CA
#   
#
#
#########################################################################

import os
import arcpy
import uuid
  

def CalcGUID():
    """Calculate a GUID and return the GUID as a string."""
    return '{' + str(uuid.uuid4()).upper() + '}'

arcpy.env.overwriteOutput = True

inFeatures = arcpy.GetParameterAsText(0)

outputFile = arcpy.GetParameterAsText(1)
if not outputFile.endswith(".shp"):
    outputFile = outputFile + ".shp"

# The input parameter is a semicolon delimited string of feature classes. Split this string on semicolon to create
# a list of input feature classes
inFeatures = inFeatures.split(";")

# If the output file is already an absolute path, use the path as is. Otherwise interpret the path
# relative to the first input file.
if os.path.isabs(outputFile):
    outFeatures = outputFile
else:
    outputDir = os.path.dirname(inFeatures[0].strip("'"))
    outFeatures = os.path.join(outputDir, outputFile)

# Declare lists to collect polygon features and non-polygons features
polygons = []
bufferedFeatures = []

try:
    # Loop through each feature class. Create buffers for points and lines, and repair geometry for all features.
    arcpy.SetProgressorLabel("Buffering features and repairing geometry...") 
    for feature in inFeatures:
        # Strip quotation marks from the file name
        feature = feature.strip("'")

        # Add a buffer if the feature is a Point or Polyline
        desc = arcpy.Describe(feature)
        if desc.shapeType in ("Point", "Polyline"):
            # Generate a name for a temporary file. The buffered data will be written to this file, and the
            # temp file will be deleted when the script exits.
            buffered = arcpy.CreateScratchName("temp", "", "featureclass", os.path.dirname(feature))
       
            arcpy.AddMessage("Buffering " + os.path.basename(feature) + "...")
            arcpy.Buffer_analysis(feature, buffered, "BuffDistM", "FULL", "ROUND", "NONE", "")
            bufferedFeatures.append(buffered)
            feature = buffered
        else:
            polygons.append(feature)
        
           
    # Merge input features
    arcpy.SetProgressorLabel("Merging features...") 
    arcpy.Merge_management(polygons + bufferedFeatures, outFeatures, "")

    # Repair feature geometry
    arcpy.SetProgressorLabel("Repairing geometry...")
    arcpy.RepairGeometry_management(outFeatures, "KEEP_NULL")   

    # Add the GlobalID field and compute a new GUID
    arcpy.SetProgressorLabel("Adding GUID field...")
    arcpy.AddField_management(outFeatures, "GlobalID", "TEXT", "", "", "50", "", "NON_NULLABLE", "NON_REQUIRED", "")

    # This method seems to be giving an error on defining the CalcGUID
    #arcpy.CalculateField_management(outFeatures, "GlobalID", "CalcGUID()", "PYTHON_9.3", "")
    # But this seems to work ok
    arcpy.SetProgressorLabel("Calculating GUID field...")
    arcpy.CalculateField_management(outFeatures, "GlobalID", "CalcGUID()", "PYTHON_9.3", "def CalcGUID():\\n  import uuid\\n  return '{' + str(uuid.uuid4()).upper() + '}'\\n")

    # Add and calculate the Gross Infected Area field
    arcpy.SetProgressorLabel("Adding GIA field...")
    arcpy.AddField_management(outFeatures, "GIA", "DOUBLE", "", "", "", "", "NON_NULLABLE", "NON_REQUIRED", "")
    arcpy.SetProgressorLabel("Calculating GIA...")
    arcpy.CalculateField_management(outFeatures, "GIA", "!shape.area@acres!", "PYTHON_9.3", "")

    # Add and calculate the Net Infected Area field
    arcpy.SetProgressorLabel("Adding NIA field...")
    arcpy.AddField_management(outFeatures, "NIA", "DOUBLE", "", "", "", "", "NON_NULLABLE", "NON_REQUIRED", "")
    arcpy.SetProgressorLabel("Calculating NIA...")
    arcpy.CalculateField_management(outFeatures, "NIA", "!GIA! * !PercCov!", "PYTHON_9.3", "")

    arcpy.AddMessage("Done, output written to " + outFeatures)
    
finally:    
    # Delete intermediate data sets
    for feature in bufferedFeatures:
        try:
            arcpy.Delete_management(feature)
        except:
            arcpy.AddMessage("Unable to delete intermediate data: " + feature)
