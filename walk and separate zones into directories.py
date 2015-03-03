# This walk script finds zone 10 and zone 11 shapefiles scattered throughout the directories and copied them into their respective zone 10 and zone 11 folders.  This organized them by zone so I could merge them all together.
# It could easily be adapted to to do whatever you wanted to featureclasses within a directory system. Feel free to modify the code block that "does stuff"
# 
# Author: R. Rudolph, National Park Service
# Date: 3/20/14

import arcpy, os

# Set to True if you want to overwrite files that may be in the output directories. 
arcpy.env.overwriteOutput = False


# This function courtesy ESRI's arcpy.wordpress.com which is a great resource, by the way. 
def inventory_data(workspace, datatypes):
    """
    Generates full path names under a catalog tree for all requested
    datatype(s).
 
    Parameters:
    workspace: string
        The top-level workspace that will be used.
    datatypes: string | list | tuple
        Keyword(s) representing the desired datatypes. A single
        datatype can be expressed as a string, otherwise use
        a list or tuple. See arcpy.da.Walk documentation 
        for a full list.
    """
    for path, path_names, data_names in arcpy.da.Walk(workspace, datatype=datatypes):
        for data_name in data_names:
            yield os.path.join(path, data_name)
 

try:
    for fc in inventory_data(r"C:\Temp\QUTO Laura KV files", "FeatureClass"):
        print fc
   
        ### This block "Does Stuff." In this case, we are copying shapefiles that meet are a type of UTM projection. You can do whatever you want to the files you are walking. 

        # Folders to copy files
        zone10 = r"C:\Temp\QUTOcopy\zone10"
        zone11 = r"C:\Temp\QUTOcopy\zone11"

        desc = arcpy.Describe(fc)
        if desc.spatialReference.name == "NAD_1927_UTM_Zone_10N":
            print "Copying " + fc + " to: " + zone10
            arcpy.CopyFeatures_management(fc, zone10 + "\\" + desc.name)
        elif desc.spatialReference.name == "NAD_1927_UTM_Zone_11N":
            print "Copying " + fc + " to: " + zone11
            arcpy.CopyFeatures_management(fc, zone11 + "\\" + desc.name)


except Exception as e:
    # If an error occurred, print line number and error message
    import traceback
    import sys
    tb = sys.exc_info()[2]
    print "Line {0}".format(tb.tb_lineno)
    print e.message

    #If using in an ArcCatalog tool
    #arcpy.AddMessage("Line {0}".format(tb.tb_lineno))
    #arcpy.AddMessage(e.message)
