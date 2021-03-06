##---------------------------------------------------------------------
## ImportARGOS.py
##
## Description: Read in ARGOS formatted tracking data and create a line
##    feature class from the [filtered] tracking points
##
## Usage: ImportArgos <ARGOS folder> <Output feature class> 
##
## Created: Fall 2020
## Author: taylor.stoni@duke.edu 
##---------------------------------------------------------------------

# Import modules
import sys, os, arcpy

#Allow arcpy to overwrite outputs 
arcpy.env.overwriteOutput = True

# Set input variables (Hard-wired)
#inputFile = 'V:\\ARGOSTracking\\Data\\ARGOSData\\1997dg.txt'
inputFolder = "V:\\ARGOSTracking\\Data\\ARGOSdata"
outputFC = "V:/ARGOSTracking/Scratch/ARGOStrack.shp"
outputSR = arcpy.SpatialReference(54002)

#Create an empty feautre class to which we will add features
outPath, outName = os.path.split(outputFC) #splits output path and output file name
arcpy.CreateFeatureclass_management(outPath, outName, "POINT", '','', '', outputSR)

# Add TagID, LC, IQ, and Date fields to the output feature class
arcpy.AddField_management(outputFC,"TagID","LONG")
arcpy.AddField_management(outputFC,"LC","TEXT")
arcpy.AddField_management(outputFC,"Date","TEXT")

#Create an insert cursor 
cur = arcpy.da.InsertCursor(outputFC, ['Shape@', 'TagID', 'LC', 'Date'])

#Iterate through each ARGOS file in the user supplied folder
inputFiles = os.listdir(inputFolder) 
for inputFile in inputFiles:
    #Dont't process README.txt file 
    if inputFile == 'README.txt':
        continue
    
    #Add fill path to input file name 
    inputFile_full = os.path.join(inputFolder, inputFile)
    print(f"Processing {inputFile}")
    
    # Open the ARGOS data file for reading
    inputFileObj = open(inputFile_full,'r')
    
    # Get the first line of data, so we can use a while loop
    lineString = inputFileObj.readline()
    while lineString:
        
        # Set code to run only if the line contains the string "Date: "
        if ("Date :" in lineString):
            
            # Parse the line into a list
            lineData = lineString.split()
            
            # Extract attributes from the datum header line
            tagID = lineData[0]
            obsDate = lineData[3]
            obsTime = lineData[4]
            obsLC = lineData[7]
            
            # Extract location info from the next line
            line2String = inputFileObj.readline()
            
            # Parse the line into a list
            line2Data = line2String.split()
            
            # Extract the date we need to variables
            obsLat = line2Data[2]
            obsLon= line2Data[5]
    
            #Try to convert the coordinates to numbers
            try:
    
                # Convert raw coordinate strings to numbers
                if obsLat[-1] == 'N':
                    obsLat = float(obsLat[:-1])
                else:
                    obsLat = float(obsLat[:-1] * -1)
                if obsLon[-1] == 'W':
                    obsLon = float(obsLon[:-1])
                else:
                    obsLon = float(obsLon[:-1] * -1)
                   
                # Construct a raw point object from the feature class
                obsPoint = arcpy.Point()
                obsPoint.X = obsLon
                obsPoint.Y = obsLat
    
            #Handle any error
            except Exception as e:
                pass
                #print("Error adding record {} to the output".format(tagID))
            
            # Convert the point to a point geometry object with spatial reference
            inputSR = arcpy.SpatialReference(4326)
            obsPointGeom = arcpy.PointGeometry(obsPoint,inputSR)
            
            #Add a feature using our insert cursor
            feature = cur.insertRow((obsPointGeom,tagID,obsLC,obsDate.replace(".","/") + " " + obsTime))
            
        # Move to the next line so the while loop progresses
        lineString = inputFileObj.readline()
        
    #Close the file object
    inputFileObj.close()

#Delete the cursor
del cur
