# Description: Test script and toolbox tool for populating a DNRGPS garmin shapefile export with basic data about hydrology surveying on Santa Rosa Island, California.  
# In addition, it auto-appends the name of the watershed to each point and copies and renames image files that were taken with the survey team.
# Contact me if you would like the toolbox tool that I used to interface with this script.
# ---------------------------------------------------------------------------
# Author: R. Rudolph, National Park Service
# Date: 3/2/15


# Import modules
import arcpy, os, sys, datetime, glob, shutil
from dateutil.parser import parse

arcpy.env.overwriteOutput = True

# Get all the stuff needed from the tool dialog
inFeature = arcpy.GetParameterAsText(0)
GPSID = arcpy.GetParameterAsText(1)
surveyDate = arcpy.GetParameterAsText(2)
collectionDir = arcpy.GetParameterAsText(3)
teamMembers = arcpy.GetParameterAsText(4)
inTrack = arcpy.GetParameterAsText(5)
photoFolder = arcpy.GetParameterAsText(6)

# Get current date to put into upload date field in database
now = datetime.datetime.today()
DateUpload = now.strftime("%m/%d/%y %H:%M:%S")

# Format the input survey date so it can be used in renaming the jpg files
surveyDateFormat = parse(surveyDate).strftime("%Y-%m-%d")
	
# Setup paths so they don't have to be hard coded. That way you can move the script and folder around and not have to change it all the time.
scriptpath = sys.path[0]
toolpath = os.path.dirname(scriptpath)

# Main files for storage of survey data
fc = os.path.join(toolpath, "SRI_StreamMapping.mdb", "SRI_Stream_Survey_pts")
fcTrack = os.path.join(toolpath, "SRI_StreamMapping.mdb", "SRI_Stream_Survey_tracks")

# This watersheds file is used for doing a spatial join on the data to automatically get the watershed name. It's optional, but nice. 
SRIwatershed = os.path.join(toolpath, "SRI_StreamMapping.mdb", "SRI_Watersheds")

# Scratch geodatabase for temporary processing of data
scratchJoin = os.path.join(toolpath, "scratch.gdb", "scratchJoin")

# This is where all the photos will be dumped with formated file name
masterPhotoFolder = os.path.join(toolpath, "MasterPhotos")

try:
	# If the photo folder is not specified, then skip.  Otherwise go through and rename and copy the jpg files.
	if photoFolder == "":
		pass
	else:
		def rename(dir, pattern, titlePattern):
			for pathAndFilename in glob.iglob(os.path.join(dir, pattern)):
				title, ext = os.path.splitext(os.path.basename(pathAndFilename))
				os.rename(pathAndFilename, os.path.join(dir, titlePattern % title + ext))
		
		# Rename the jpg files in the specified folder.
		rename(photoFolder, r'*.jpg', surveyDateFormat + "_" + teamMembers + "_" + GPSID + "_" + r'%s')

		# Copy those renamed folders to the master photo folder. 
		src_files = os.listdir(photoFolder)
		for file_name in src_files:
			full_file_name = os.path.join(photoFolder, file_name)
			if (os.path.isfile(full_file_name)):
				shutil.copy(full_file_name, masterPhotoFolder)

	# If no point file is specified, then skip. Otherwise, process the point file.
	if inFeature == "":
		pass
	else:
		# Add fields to shapefile
		arcpy.AddMessage("Adding fields to GPS shapefile")
		arcpy.AddField_management(inFeature,"GPS_ID","TEXT","#","#","20","#","NULLABLE","NON_REQUIRED","#")
		arcpy.AddField_management(inFeature,"SurveyDate","DATE","#","#","#","#","NULLABLE","NON_REQUIRED","#")
		arcpy.AddField_management(inFeature,"SurveyTeam","TEXT","#","#","50","#","NULLABLE","NON_REQUIRED","#")
		arcpy.AddField_management(inFeature,"CollectDir","TEXT","#","#","50","#","NULLABLE","NON_REQUIRED","#")
		arcpy.AddField_management(inFeature,"DateUpload","TEXT","#","#","20","#","NULLABLE","NON_REQUIRED","#")

		# Populate fields with items entered from the toolbox tool. 
		arcpy.AddMessage("Populating fields with GPS ID and Date")
		arcpy.CalculateField_management(inFeature,"GPS_ID", "'" + GPSID + "'","PYTHON_9.3","#")
		arcpy.CalculateField_management(inFeature,"SurveyDate", "'" + surveyDate + "'","PYTHON_9.3","#")
		arcpy.CalculateField_management(inFeature,"SurveyTeam", "'" + teamMembers + "'","PYTHON_9.3","#")
		arcpy.CalculateField_management(inFeature,"CollectDir", "'" + collectionDir + "'","PYTHON_9.3","#")
		arcpy.CalculateField_management(inFeature,"DateUpload", "'" + DateUpload + "'","PYTHON_9.3","#")
		
		# Create field mappings
		fieldmappings = arcpy.FieldMappings()
		fieldmappings.addTable(inFeature)
		fieldmappings.addTable(SRIwatershed)

		# Use the field mappings to do a spatial join to auto extract the watershed name. 
		arcpy.AddMessage("Performing spatial join with watershed file to auto-extract watershed name")
		arcpy.SpatialJoin_analysis(inFeature,SRIwatershed,scratchJoin,"JOIN_ONE_TO_ONE","KEEP_ALL", fieldmappings)

		# Copy the joined scratch featureclass back to the original file
		arcpy.AddMessage("Replacing orignal file with watershed named join file")
		arcpy.CopyFeatures_management(scratchJoin, inFeature)

		# Process: Append processed file to master database
		arcpy.Append_management(inFeature, fc, "NO_TEST", "", "")
		arcpy.AddMessage("Appended GPS data to WetDry database")


	# Now do all the same stuff you did for the survey file to the track, then upload that track to the database.  This is mostly copy and paste from the above field adding section
	if inTrack == "":
		pass
	else:
		# add fields to track shapefile
		arcpy.AddMessage("Adding fields to GPS track")
		arcpy.AddField_management(inTrack,"GPS_ID","TEXT","#","#","20","#","NULLABLE","NON_REQUIRED","#")
		arcpy.AddField_management(inTrack,"SurveyDate","DATE","#","#","#","#","NULLABLE","NON_REQUIRED","#")
		arcpy.AddField_management(inTrack,"SurveyTeam","TEXT","#","#","50","#","NULLABLE","NON_REQUIRED","#")
		arcpy.AddField_management(inTrack,"CollectDir","TEXT","#","#","50","#","NULLABLE","NON_REQUIRED","#")
		arcpy.AddField_management(inTrack,"DateUpload","TEXT","#","#","20","#","NULLABLE","NON_REQUIRED","#")

		arcpy.AddMessage("Populating fields with GPS ID and Date")
		arcpy.CalculateField_management(inTrack,"GPS_ID", "'" + GPSID + "'","PYTHON_9.3","#")
		arcpy.CalculateField_management(inTrack,"SurveyDate", "'" + surveyDate + "'","PYTHON_9.3","#")
		arcpy.CalculateField_management(inTrack,"SurveyTeam", "'" + teamMembers + "'","PYTHON_9.3","#")
		arcpy.CalculateField_management(inTrack,"CollectDir", "'" + collectionDir + "'","PYTHON_9.3","#")
		arcpy.CalculateField_management(inTrack,"DateUpload", "'" + DateUpload + "'","PYTHON_9.3","#")

		# Process: Append processed track file to master database
		arcpy.Append_management(inTrack, fcTrack, "NO_TEST", "", "")
		arcpy.AddMessage("Appended GPS track data to WetDry database")

	arcpy.AddMessage("Script completed")
	
except Exception as e:
	# If an error occurred, print line number and error message
	import traceback
	import sys
	tb = sys.exc_info()[2]
	arcpy.AddMessage("Line {0}".format(tb.tb_lineno))
	arcpy.AddMessage(e.message)