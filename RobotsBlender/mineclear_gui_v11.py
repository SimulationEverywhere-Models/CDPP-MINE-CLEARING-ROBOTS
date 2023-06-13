#!BPY

""" Registration info for Blender menus:
Name: 'CD++ Simulations'
Blender: 241
Group: 'Simulations'
Tooltip: 'CD++ Simulations2'
"""

# --------------------------------------------------------------------------
# ***** BEGIN GPL LICENSE BLOCK *****
#
# Copyright (C) 2007 Emil Poliakov aka NiTeC
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# 
#
# ***** END GPL LICENCE BLOCK *****
# --------------------------------------------------------------------------

__author__ = "Emil Poliakov"
__version__ = "1.0.2"

# --------------------------------------------------------------------------        
# Modified by Kin Wing Tsui - Dec 2007
# To animate the auto factory DEVS model
#
# Modified by Patrick Castonguay - 4 Sept 2008
# To animate the aircraft evacuation model
#   Fixed file openning and closing to prevent buffer overrun
#   Added the parsing of .ma and .val files
#   Added the logging of information to a file
#
# Modified by Tania Pendergast - Nov 2008
# For animation of minefield mapping model
# --------------------------------------------------------------------------

__bpydoc__ = """
CD++ Simulations 1.0.2

With this script you can load the CD++ Simulations results into Blender and apply them to objects etc.

Select the proper .MA and .LOG file via the graphical interface

If refence to a .val file is made, the file is also parsed and initial values used to set visualisation
"""

import Blender  # This will import the library of blender functions we will use
#import bpy
from Blender import Draw, BGL, Window, Image, Scene, Material

winsize = Window.GetAreaSize()
scn = Scene.GetCurrent()
#scn = bpy.data.scenes.active
# myimage = Image.Load('c:\cd.jpg')

defaultPath = "c:/Program Files/Blender Foundation/Blender/.Blender/"
logFileName = defaultPath+"MineClear4Robots.log"
maFileName = defaultPath+"MineClear4Robots.ma"
valfilename = ""
defaultValue = 0

# --------------------------------------------------------------------------
# read_val(path)
#
# Read and parse CD++ val file
#   Setup initial values for visual environment
#
# path : full path of the CD++ val file
# --------------------------------------------------------------------------
def read_val(path):
        global datalogfile
        datalogfile.write("\n\n***************\nReading file "+path+"\n")
        
        Blender.Window.WaitCursor(1)
        try:
            valFile = open(path, "r")
        except:
            datalogfile.write("    Error in read_val("+path+")\n")
            return
        
        # Look for cell information in order to draw start state
        for line in valFile.readlines():
            words = line.split('=')
            # Will be true if '=' is found on line  
            if len(words) >= 2:
                time = "00:00:00:000"
                cell = words[0]
                logValueWord = words[1]
                try:
                    apply_log(cell.strip(), time, logValueWord.strip())
                except:
                    valFile.close()
                    #cdppLogFile.close()
        valFile.close()
        Blender.Window.WaitCursor(0)

# --------------------------------------------------------------------------
# read_ma(path)
#
# Read and parse CD++ ma file
#   Currently only looks for the .val file to setup visual environment
#
# path : full path of the CD++ ma file
# --------------------------------------------------------------------------
def read_ma(path):
        global datalogfile, valfilename, defaultValue
        datalogfile.write("\n\n***************\nReading file "+path+"\n")
        
        Blender.Window.WaitCursor(1)
        try:
            maFile = open(path, "r")
        except:
            datalogfile.write("    Error in read_ma("+path+")\n")
            return
        
        # Look for a .val file and for default initial values
        for line in maFile.readlines():
                words = line.split()
                # Keywords are expected to be first word of line
                if len(words) > 0:
                    if words[0] == ("initialvalue"):
                        defaultValue = words[2]
                    elif words[0] == ("initialCellsValue"):
                        valfilename = defaultPath+words[2]
                        read_val(valfilename)
        maFile.close()
        Blender.Window.WaitCursor(0)

# --------------------------------------------------------------------------
# read_log(path)
#
# Read and parse CD++ log file
#
# path : full path of the CD++ log file
# --------------------------------------------------------------------------
def read_log(path):
        global datalogfile
        datalogfile.write("\n\n***************\nReading file "+path+"\n")
        
        Blender.Window.WaitCursor(1)
        try:
            cdppLogFile = open(path, "r")
        except:
            datalogfile.write("    Error in read_log("+path+")\n")
            return

        # Look for messages in the CD++ log file
        for line in cdppLogFile.readlines():
                words = line.split()
                # For mineclear only Y messages are processed
                if (len(words) > 1) and (words[1] == ("Y")):
                        time          = words[3]
                        cell          = words[5]
                        #port          = words[7]
                        logValueWord = words[9]
                        try:
                            apply_log(cell.strip(), time, logValueWord.strip())
                        except:
                            cdppLogFile.close()
        cdppLogFile.close()
        Blender.Window.WaitCursor(0)

#add robot fn
#remove robot fn
#change material fn

# ----------------------------------------------------------------------------------
# apply_log(cell, time, logValueWord)
#
# Interpret CD++ log file data for Blender visualization
#
# cell :            cell to be handled
# time :            timestamp of the CD++ log file message
# logvalueWord :    string containing the numeric value in the CD++ log file message
# -----------------------------------------------------------------------------------
def apply_log(cell, time, logValueWord):
        global datalogfile
        datalogfile.write("Simulation time:"+time+", Processing "+cell+" with value "+logValueWord+"\n")

        # Time expected to be in CD++ format of 00:00:00:000; change it for Blender
        # It is used as a frame setup.  For mineclear the increment used is mseconds
        hours = (time[0:2])
        minutes = (time[3:5])
        seconds = (time[6:8])
        mseconds = (time[9:12])
        totaltime = (int(hours)*36000 + int(minutes)*600 + int(seconds)*10 + int(mseconds)/100)
        Blender.Set('curframe',totaltime)
        
        # Retrieval of the cell description currently works for three dimensions
        # cells are always described as 'modelName'(x,y,z)(..)
        # zeroize the position counters to be more versatile than previous version
        a = b = c = d = 0
        for i in range(len(cell)):
                if cell[i]=='(' and cell[i-1]!=')':
                        a = i
                elif cell[i]==',' and b==0:
                        b = i
                elif cell[i]==',':
                        c = i
                elif cell[i]==')' and d==0:
                        d = i
                        
        # Transform description into coordinate                        
        xcoord = (cell[a+1:(a+len(range(a,b)))])
        ycoord = (cell[b+1:(b+len(range(b,c)))])
        zcoord = (cell[c+1:(c+len(range(c,d)))])
        
        # Only first plane is used in mineclear simulation to represent movement
        # the other is used for background calculation within the CD++ model
        if int(zcoord) != 0:
                 return #Exit the function apply_log()

        # Here we truncate the decimal portion as the value is expected to be an integer  
        logend = len(logValueWord)
        for j in range(len(logValueWord)):
                if logValueWord[j]=='.':
                        logend = j
        logValue = int(logValueWord[0:logend])
         
        try: 
                minefieldCellName = ("MFd_Cell_%s_%s_%s" %( xcoord, ycoord, zcoord) )
                robotName = ("Robot_Cell_%s_%s_%s" %( xcoord, ycoord, zcoord) )
                datalogfile.write("  ** Processing: logValue %d, minefieldCellName:%s, robotname:%s\n " %(logValue, minefieldCellName, robotName) )
        except:
                datalogfile.write("Exception in format string\n")

        scene_obs = list(scn.objects)
        datalogfile.write("Objects in scene are: %s" %(scene_obs) )

        # Process state values that are passed as logValue for the current cell
        try:                
            if (logValue == 20):
                #No robot, cell not scanned
                #When drawing the initial minefield map, all cells should be grey
                #No change to robots (there is not one in the cell)
                try:
                        #minefieldCell = [o for o in scn.objects if o.name == "Cube"][0]
                        datalogfile.write("    Processing: %s for %d\n" %(minefieldCellName, logValue) )
                        #Add an unscanned cell   
                        minefieldCell = Blender.Object.Get('Cube.Unscanned')
                        if( minefieldCell not in scene_obs ):
                                scn.objects.link(minefieldCell)
                        minefieldCell.select(1)
                        Blender.Object.Duplicate()
                        activeObject = scn.getActiveObject()
                        activeObject.name = minefieldCellName
                        activeObject.LocX = int(xcoord)
                        activeObject.LocY = int(ycoord)
                        activeObject.LocZ = int(zcoord)
                        activeObject.select(0)
                        datalogfile.write("    **Object minefieldCell created at (%s,%s,%s)\n" %(xcoord, ycoord, zcoord) )
                except:
                        datalogfile.write("    **logValue 20 - Object minefieldCell already exists or error occured**\n")          

            elif (logValue == 120) and (time == "00:00:00:000"):
                #Add a robot and an unscanned cell.
                try:
                        #robot = [o for o in scn.objects if o.name == "Robot"][0]
                        datalogfile.write("    Processing: %s for %d\n" %(robotName, logValue) )
                        #Add a robot
                        robot = Blender.Object.Get('Robot')
                        if( robot not in scene_obs ):
                                scn.objects.link(robot)
                        robot.select(1)
                        Blender.Object.Duplicate()
                        activeObject = scn.getActiveObject()
                        activeObject.name = robotName
                        activeObject.LocX = int(xcoord)
                        activeObject.LocY = int(ycoord)
                        activeObject.LocZ = int(zcoord) + 0.55
                        activeObject.select(0)
                        datalogfile.write("    Object Robot created at (%s,%s,%s)\n" %(xcoord, ycoord, zcoord) )
                        #Add an unscanned cell
                        datalogfile.write("    Processing: %s for %d\n" %(minefieldCellName, logValue) )
                        minefieldCell = Blender.Object.Get('Cube.Unscanned')
                        if( minefieldCell not in scene_obs ):
                                scn.objects.link(minefieldCell)
                        minefieldCell.select(1)
                        Blender.Object.Duplicate()
                        activeObject = scn.getActiveObject()
                        activeObject.name = minefieldCellName
                        activeObject.LocX = int(xcoord)
                        activeObject.LocY = int(ycoord)
                        activeObject.LocZ = int(zcoord)
                        activeObject.select(0)
                        datalogfile.write("    Object minefieldCell created at (%s,%s,%s)\n" %(xcoord, ycoord, zcoord) )
                except:
                        datalogfile.write("    ****logValue 120 with time 0 - Object Robot already exists, or error occured**\n")
                           
            elif (logValue == 120) and (time != "00:00:00:000"):
            #Only add a robot, unscanned cell already exists
                try:
                        #robot = [o for o in scn.objects if o.name == "Robot"][0]
                        datalogfile.write("    Processing: %s for %d\n" %(robotName, logValue) )
                        
                        #Add a new robot
                        robot = Blender.Object.Get ('Robot')
                        if( robot not in scene_obs ):
                                scn.objects.link(robot)
                        robot.select(1)
                        Blender.Object.Duplicate()
                        activeObject = scn.getActiveObject()
                        activeObject.name = robotName
                        activeObject.LocX = int(xcoord)
                        activeObject.LocY = int(ycoord)
                        activeObject.LocZ = int(zcoord) + 0.55
                        activeObject.select(0)
                        datalogfile.write("    Object Robot created at (%s,%s,%s)\n" %(xcoord, ycoord, zcoord) )
                except:
                        datalogfile.write("    **logValue 120 - Object Robot already exists, or error occured**\n")   

            elif (logValue == 100):
            #No mine, robot, cell scanned
            #Add a robot
            #No cell colour change because 100 denotes the fact that a robot moved into an already scanned cell with no mine
                try:
                        #robot = [o for o in scn.objects if o.name == "Robot"][0]
                        datalogfile.write("    Processing: %s for %d\n" %(robotName, logValue) )

                        #Add a new robot
                        robot = Blender.Object.Get ('Robot')
                        if( robot not in scene_obs ):
                                scn.objects.link(robot)
                        robot.select(1)
                        Blender.Object.Duplicate()
                        activeObject = scn.getActiveObject()
                        activeObject.name = robotName
                        activeObject.LocX = int(xcoord)
                        activeObject.LocY = int(ycoord)
                        activeObject.LocZ = int(zcoord) + 0.55
                        activeObject.select(0)
                        datalogfile.write("    Object Robot created at (%s,%s,%s)\n" %(xcoord, ycoord, zcoord) )        
                except:
                        datalogfile.write("    **logValue 100 - Object Robot already exists, or error occured**\n")      

            elif (logValue == 110):
            #Mine, robot, cell scanned
            #Add a robot
            #No cell colour change because 110 denotes the fact that a robot moved into an already scanned cell with a mine
                try:
                        #robot = [o for o in scn.objects if o.name == "Robot"][0]
                        datalogfile.write("    Processing: %s for %d\n" %(robotName, logValue) )  

                        #Add a new robot
                        robot = Blender.Object.Get ('Robot')
                        if( robot not in scene_obs ):
                                scn.objects.link(robot)
                        robot.select(1)
                        Blender.Object.Duplicate()
                        activeObject = scn.getActiveObject()
                        activeObject.name = robotName
                        activeObject.LocX = int(xcoord)
                        activeObject.LocY = int(ycoord)
                        activeObject.LocZ = int(zcoord) + 0.55
                        activeObject.select(0)
                        datalogfile.write("    Object Robot created at (%s,%s,%s)\n" %(xcoord, ycoord, zcoord) )         
                except:
                        datalogfile.write("    **logValue 110 - Object Robot already exists, or error occured**\n")      

            elif (logValue == 0):
            #No mine, no robot, cell already scanned
            #Remove robot 
            #No colour change, cell is already scanned
                try:
                        datalogfile.write("    Processing: %s for %d\n" %(minefieldCellName, logValue) )
                        ob = Blender.Object.Get(robotName)
                        if ( ob in scene_obs ):
                                ob.select(1)
                                activeObject = scn.getActiveObject()
                                activeObject.name = "unlinked_robot"
                                datalogfile.write("     Renamed robot to %s before unlinking.\n" %(activeObject) )
                                scn.objects.unlink(activeObject)
                                datalogfile.write("    Unlinked robot\n")
                        datalogfile.write("    Cell was already scanned, no change to minefield cell...robot removed if there was one\n")
                except:
                        datalogfile.write("    **Error occured with already scanned cell**\n")           

            elif (logValue == 10):
            #Mine, no robot, cell already scanned
            #Remove robot
            #No colour change, cell is already scanned          
                try:
                        datalogfile.write("    Processing: %s for %d\n" %(minefieldCellName, logValue) )
                        ob = Blender.Object.Get(robotName)
                        if ( ob in scene_obs ):
                                ob.select(1)
                                activeObject = scn.getActiveObject()
                                activeObject.name = "unlinked_robot"
                                datalogfile.write("     Renamed robot to %s before unlinking.\n" %(activeObject) )
                                scn.objects.unlink(activeObject)
                                datalogfile.write("    Unlinked robot\n")
                        datalogfile.write("    Cell was already scanned, no change to minefield cell...robot removed if there was one\n")
                except:
                        datalogfile.write("    **Error occured with already scanned cell**\n")           
             
            elif (logValue == 201) or (logValue == 202) or (logValue == 203) or (logValue == 204):
                #No mine, robot about to move, cell scanned
                #Already a robot in the cell (keep robot)
                #Change cell colour to green to show that the cell was just scanned and no mine was found
                try:
                        #Remove old unscanned cell
                        datalogfile.write("    Processing: %s for %d\n" %(minefieldCellName, logValue) ) 
                        ob = Blender.Object.Get(minefieldCellName)
                        if ( ob in scene_obs ):
                                ob.select(1)
                                activeObject = scn.getActiveObject()
                                activeObject.name = "unlinked_cell"
                                datalogfile.write("     Renamed cell to %s before unlinking.\n" %(activeObject) )
                                scn.objects.unlink(activeObject)
                                datalogfile.write("    Unlinked old unscanned cell\n")
                         
                        #Add the appropriate scanned cell
                        minefieldCell = Blender.Object.Get('Cube.Nomine')
                        if( minefieldCell not in scene_obs ):
                                scn.objects.link(minefieldCell)
                                datalogfile.write("     Cube.Nomine was not already linked\n")
                        else:
                                datalogfile.write("     Cube.Nomine was already linked\n")

                        minefieldCell.select(1)
                        Blender.Object.Duplicate()
                        activeObject = scn.getActiveObject()
                        activeObject.name = minefieldCellName
                        activeObject.LocX = int(xcoord)
                        activeObject.LocY = int(ycoord)
                        activeObject.LocZ = int(zcoord)
                        activeObject.select(0)
                        datalogfile.write("    Cell scanned and no mine found. New object minefieldCell created at: (%s,%s,%s)" %(xcoord, ycoord, zcoord) )
                except:
                        datalogfile.write("    **Error occured with cell material change** \n " ) 

            elif (logValue == 211) or (logValue == 212) or (logValue == 213) or (logValue == 214):
            #Mine, robot about to move, cell scanned
            #Already a robot in the cell (keep robot)
            #Change cell colour to red to show that the cell was just scanned and a mine was found
                try:
                        #Remove old unscanned cell
                        datalogfile.write("    Processing: %s for %d\n" %(minefieldCellName, logValue) )
                        ob = Blender.Object.Get(minefieldCellName)
                        if ( ob in scene_obs ):                        
                                ob.select(1)
                                activeObject = scn.getActiveObject()
                                activeObject.name = "unlinked_cell"
                                datalogfile.write("     Renamed cell to %s before unlinking.\n" %(activeObject) )
                                scn.objects.unlink(activeObject)
                                datalogfile.write("    Unlinked old unscanned cell\n")                        
                        #Add the appropriate scanned cell                        
                        minefieldCell = Blender.Object.Get('Cube.Mine')
                        if( minefieldCell not in scene_obs ):
                                scn.objects.link(minefieldCell)
                                datalogfile.write("     Cube.Mine was not Already linked\n")
                        else:
                                datalogfile.write("     Cube.Mine was already linked\n")
                                                        
                        minefieldCell.select(1)
                        Blender.Object.Duplicate()
                        activeObject = scn.getActiveObject()
                        activeObject.name = minefieldCellName
                        activeObject.LocX = int(xcoord)
                        activeObject.LocY = int(ycoord)
                        activeObject.LocZ = int(zcoord)
                        activeObject.select(0)
                        datalogfile.write("    Cell scanned and mine found. New object minefieldCell created at: (%s,%s,%s)" %(xcoord, ycoord, zcoord) )                        
                except:
                        datalogfile.write("    **Error occured with cell material change**\n") 
            else:
                datalogfile.write("    **Log value not recognized as valid: %d**\n" %(logValue))

        except:
            datalogfile.write("\n\n\n")
            datalogfile.write("****************************************\n")
            datalogfile.write("* Unexpected stop in the logging sequence   *\n")
            datalogfile.write("*   in apply_log() portion of script   *\n")            
            datalogfile.write("****************************************\n")
            datalogfile.close()
            
        # Refresh the display
        scn.update()
        Blender.Redraw()
        datalogfile.write("  **Done Apply_Log\n\n")
#        print 'The current frame is:' , Blender.Get('curframe'), " !!!END OF SCRIPT!!!"

# --------------------------------------------------------------------------
# import_maFile(ma)
#
# Saves the CD++ MA file path
#
# ma : MA file path to be saved
# --------------------------------------------------------------------------    
def import_maFile(ma):
        global maFileName
        maFileName = ma
        Draw.Redraw(1)

# --------------------------------------------------------------------------
# import_logFile(log)
#
# Saves the CD++ log file path
#
# log : log file path to be saved
# --------------------------------------------------------------------------    
def import_logFile(log):
        global logFileName
        logFileName = log
        Draw.Redraw(1)

# --------------------------------------------------------------------------
# event(evt, val)
#
# Keyboard and mouse event handler
# -------------------------------------------------------------------------- 
def event(evt, val):  
     return

# --------------------------------------------------------------------------
# buttonHandler(evt)
#
# Button-click handler
# Handles .ma and .log file Browse Buttons as well as Execute Button
# --------------------------------------------------------------------------
def buttons(evt): 
    global logFileName, maFileName, datalogfile, defaultPath
    default_name = Blender.Get('filename')
   # if default_name.endswith('untitled.blend'):
   # Could add handling for file path default setup
    ma_name = default_name[0:len(default_name)-len("untitled.blend")] + ('*.ma')
    log_name = default_name[0:len(default_name)-len("untitled.blend")] + ('*.log')
    if evt == 1:
        Blender.Window.FileSelector(import_maFile, "Select",ma_name)
    if evt == 2:
        Blender.Window.FileSelector(import_logFile, "Select", log_name)
    if evt == 3:
        #TODO disable Execute button
        # Set file where debugging and execution information will be saved
        datalogfile = open("c:/tmp/data_logger.txt", "w")
        datalogfile.write("****************************\n")
        datalogfile.write("* Start of logging sequence *\n")
        datalogfile.write("****************************\n\n\n")
        print "Executing CD++/Blender Simulation Visualization Tool..."
        
        read_ma(maFileName)
        read_log(logFileName)
        
        print "Execution complete, see data log file for details:\n   ", datalogfile.name
        datalogfile.write("\n\n\n")
        datalogfile.write("****************************\n")
        datalogfile.write("* End of logging sequence   *\n")
        datalogfile.write("****************************\n")
        datalogfile.close()

        BGL.glClearColor(0,0,0,1)
        BGL.glClear(Blender.BGL.GL_COLOR_BUFFER_BIT)

# --------------------------------------------------------------------------
# gui()
#
# Main initial user interface of the script
# Sets-up the display
# --------------------------------------------------------------------------        
def gui():
    global maFileName, logFileName, loginfo
    BGL.glClearColor(0,0,0,1)
    BGL.glClear(BGL.GL_COLOR_BUFFER_BIT)
    BGL.glColor3f(1,1,1) 

    # MA Browse button setup  
    BGL.glRasterPos2i(10, (winsize[1]-100))
    text1 = Draw.Text("Select MA File", 'normal')
    log_toggle = Draw.Toggle("Browse",1,10,(winsize[1]-130),100,20,0,"Import the CD++ MA File")
    BGL.glRasterPos2i(10, (winsize[1]-160))
    text1 = Draw.Text(maFileName, 'normal')

    # LOG Browse button setup
    BGL.glRasterPos2i(10, (winsize[1]-200))
    text2 = Draw.Text("Select LOG File", 'normal')
    ma_toggle = Draw.Toggle("Browse",2,10,(winsize[1]-230),100,20,0,"Import the CD++ Generated LOG File")
    BGL.glRasterPos2i(10, (winsize[1]-260))
    text1 = Draw.Text(logFileName, 'normal')

    # Execute button setup
    execute_toggle = Draw.Toggle("Execute",3,10,(winsize[1]-350),100,20,0,"Starts the Blender Visualization")
 
    # Text at the top of the screen
    BGL.glRasterPos2i(10, (winsize[1]-20))
    Draw.Text("Welcome to the CD++/Blender", 'large')
    BGL.glRasterPos2i(10, (winsize[1]-40))
    Draw.Text("Simulation Visualization Tool", 'large')

    # Display image on the script screen
    #BGL.glBlendFunc(BGL.GL_SRC_ALPHA, BGL.GL_ONE_MINUS_SRC_ALPHA) 
    #Draw.Image(myimage, 10, winsize[1]-70)

# Register user interface and user event handlers
Blender.Draw.Register(gui, event, buttons)

#!BPY


        
