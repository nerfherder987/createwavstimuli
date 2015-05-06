import glob
import os.path
import wave
import random

clipData = []
distractData = []
silenceData = []

file_sublists = []
clipData_sublists = []

distClipList = []

currentDirectory = os.getcwd()
print(currentDirectory)

# Get list of wav files in current folder and find the index of the silence
# and distractor wav files
def createFileList():
    global distractFile
    global silenceFile
    global file_list
    
    counter = 0
    file_list = glob.glob("*.wav")
    
    for i in file_list:
        if "distractionstimuli" in i:
            distIndex = counter
            print(distIndex)
        if "silence" in i:
            silenceIndex = counter
            print(silenceIndex)
        counter = counter + 1

    # Glob seems to automatically sort based on time stamp. Oldest files first?
    distractFile = file_list.pop(distIndex)
    print(distractFile)
    silenceFile = file_list.pop(silenceIndex - 1)
    print(silenceFile)
    print(len(file_list))
    file_list.sort()

    for i in range(0, len(file_list)-1, 4):
        file_sublists.extend([file_list[i:i+4]])
        
createFileList()

# Read data from wav files into lists

def createDataLists():
    w = wave.open(distractFile,'rb')
    distractData.append( [w.getparams(), w.readframes(w.getnframes())])
    w.close()

    w = wave.open(silenceFile, 'rb')
    silenceData.append( [w.getparams(), w.readframes(w.getnframes())])
    w.close()

    for wav_file in file_list:
        #print(wav_file)
        w = wave.open(wav_file, 'rb')
        clipData.append( [w.getparams(), w.readframes(w.getnframes())])
        w.close()

    # Creates master list of clip info with each category broken into sublists
    # Should be in the form [[1A,1B,1C,1D],...[34A,34B,34C,34D]]
    for i in range(0, len(clipData)-1, 4):
        clipData_sublists.extend([clipData[i:i+4]])
        
createDataLists()

# To extract a piece of a file, read the entire file into a list, and determine
# select the part of the file to be used from the list.
# For this script, I will extract bits of the file from the distractData list
# and copy them to a "holding" list

# The first item in the sublists is the file info (tuple). The second points to
# the file's data. 

# Separate large list of files into smaller lists grouped by the number
# in the file name. e.g. [[1A,1B,1C,1D],[2A,2B,2C,2D]...etc]

# A-B, A-C, A-D, C-D, C-A, C-B
# Indexes 0:1, 0:2, 0:3, 2:3, 2:0, 2:1

# But iterate through this x number of times, where x = number of durations
# File names would be in form 1A_1B_duration

def createClips():
    # Open a text file to store list of file names
    
    #listFile = open("D:\\mp3 files\\Stimuli\\FileNames.txt", "w")
    listFile = open(".\\Stimuli\\FileNames.txt", "w")
    
    distFileLength = len(distractData[0][1])  # gets total length of data file
    
    # Out of larger distractor file, create smaller clips of different durations
    # The sample width for these files is 2 bytes, so the length of the data string
    # is duration * sample rate(44100) * 2(sample width)

    # List to store distractor chunks, declares as global varible so it can be
    # accessed by next function

    # Total number of durations: 11
    # 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6

    durationList = [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6]
    counter = 0

    for item in durationList:
        # Counter variable that indexes the unique distractor from the pool of
        # distractor clips
        uniqueDistIndex = 0
    
        # distractor file sample width x sample/frame rate x distractor duration
        distDuration = distractData[0][0][1] * distractData[0][0][2] * item

        # Maximum start time must be total length minus distractor duration, so we
        # don't go beyond the end of the clip
        maxStart = distFileLength - distDuration

        distClipList = []

        for stuff in range(156):
            startPoint = random.randint(2,maxStart - 2)  # The minus 2 is to make sure we
            # don't go past the end of the file if we have to adjust startPoint

            # Checks that starting point is even
            if startPoint % 2 <> 0:
                startPoint = startPoint + 1  # Makes startPoint even if it wasn't even before

            distClipList.append(distractData[0][1][startPoint:int(startPoint + float(distDuration))])

        # create the merged files
        for soundFile in range(len(file_sublists)):

            # A -> B
            outfile1 = '.\\Stimuli\\' + file_sublists[soundFile][0].rstrip('.wav') + "_" + \
            file_sublists[soundFile][1].rstrip('.wav') + "_" + str(int(item*1000)) + "_" + "MA" + ".wav"
            output = wave.open(outfile1, 'wb')
            output.setparams(clipData_sublists[soundFile][0][0])
            output.writeframes(clipData_sublists[soundFile][0][1])
            output.writeframes(distClipList[uniqueDistIndex])
            output.writeframes(clipData_sublists[soundFile][1][1])
            output.close()
            # Writes the name of the current file to the text file
            listFile.write(file_sublists[soundFile][0].rstrip('.wav') + "\t" + \
            file_sublists[soundFile][1].rstrip('.wav') + "\t" + str(int(item*1000)) + "\t" + "MA" + "\n")
            # Increments counter variable
            uniqueDistIndex = uniqueDistIndex + 1
            
            # A -> C
            outfile2 = '.\\Stimuli\\' + file_sublists[soundFile][0].rstrip('.wav') + "_" + \
            file_sublists[soundFile][2].rstrip('.wav') + "_" + str(int(item*1000)) + "_" + "MM" + ".wav"
            output = wave.open(outfile2, 'wb')
            output.setparams(clipData_sublists[soundFile][0][0])
            output.writeframes(clipData_sublists[soundFile][0][1])
            output.writeframes(distClipList[uniqueDistIndex])
            output.writeframes(clipData_sublists[soundFile][2][1])
            output.close()
            # Writes the name of the current file to the text file
            listFile.write(file_sublists[soundFile][0].rstrip('.wav') + "\t" + \
            file_sublists[soundFile][2].rstrip('.wav') + "\t" + str(int(item*1000)) + "\t" + "MM" + "\n")
            # Increments counter variable
            uniqueDistIndex = uniqueDistIndex + 1

            # A -> D
            outfile3 = '.\\Stimuli\\' + file_sublists[soundFile][0].rstrip('.wav') + "_" + \
            file_sublists[soundFile][3].rstrip('.wav') + "_" + str(int(item*1000)) + "_" + "MM" + ".wav"
            output = wave.open(outfile3, 'wb')
            output.setparams(clipData_sublists[soundFile][0][0])
            output.writeframes(clipData_sublists[soundFile][0][1])
            output.writeframes(distClipList[uniqueDistIndex])
            output.writeframes(clipData_sublists[soundFile][3][1])
            output.close()
            # Writes the name of the current file to the text file
            listFile.write(file_sublists[soundFile][0].rstrip('.wav') + "\t" + \
            file_sublists[soundFile][3].rstrip('.wav') + "\t" + str(int(item*1000)) + "\t" + "MM" + "\n")
            # Increments counter variable
            uniqueDistIndex = uniqueDistIndex + 1
            
            # C -> D
            outfile4 = '.\\Stimuli\\' + file_sublists[soundFile][2].rstrip('.wav') + "_" + \
            file_sublists[soundFile][3].rstrip('.wav') + "_" + str(int(item*1000)) + "_" + "MA" + ".wav"
            output = wave.open(outfile4, 'wb')
            output.setparams(clipData_sublists[soundFile][2][0])
            output.writeframes(clipData_sublists[soundFile][2][1])
            output.writeframes(distClipList[uniqueDistIndex])
            output.writeframes(clipData_sublists[soundFile][3][1])
            output.close()
            # Writes the name of the current file to the text file
            listFile.write(file_sublists[soundFile][2].rstrip('.wav') + "\t" + \
            file_sublists[soundFile][3].rstrip('.wav') + "\t" + str(int(item*1000)) + "\t" + "MA" + "\n")
            # Increments counter variable
            uniqueDistIndex = uniqueDistIndex + 1

            # progress counter
            print("Processed" + str(soundFile))

    # For 2 second duration, the randomly selected start time must be no further
    # than length - 2 sec; so if the file is 9 sec, start time can't be later than
    # 7 seconds in.

    # Closes text file
    listFile.close()

createClips()

