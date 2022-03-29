#!/usr/bin/python3

#                       ___              __                __   ____                              __                     __              
#   __                 /\_ \            /\ \__            /\ \ /\  _`\                           /\ \__                 /\ \__           
#  /\_\     ____    ___\//\ \       __  \ \ ,_\     __    \_\ \\ \ \L\ \   __  __    ___         \ \ ,_\     __     ____\ \ ,_\    ____  
#  \/\ \   /',__\  / __`\\ \ \    /'__`\ \ \ \/   /'__`\  /'_` \\ \ ,  /  /\ \/\ \ /' _ `\        \ \ \/   /'__`\  /',__\\ \ \/   /',__\ 
#   \ \ \ /\__, `\/\ \L\ \\_\ \_ /\ \L\.\_\ \ \_ /\  __/ /\ \L\ \\ \ \\ \ \ \ \_\ \/\ \/\ \        \ \ \_ /\  __/ /\__, `\\ \ \_ /\__, `\
#    \ \_\\/\____/\ \____//\____\\ \__/.\_\\ \__\\ \____\\ \___,_\\ \_\ \_\\ \____/\ \_\ \_\        \ \__\\ \____\\/\____/ \ \__\\/\____/
#     \/_/ \/___/  \/___/ \/____/ \/__/\/_/ \/__/ \/____/ \/__,_ / \/_/\/ / \/___/  \/_/\/_/  _______\/__/ \/____/ \/___/   \/__/ \/___/ 
#                                                                                            /\______\                                   
#                                                                                            \/______/                                   

################################################################################

# Provides the updateRow function wich is used in by the queue api server to
# write specific test results to the index.html page.

################################################################################

import re
from testList import checks

#Function that changes score for a student
def updateRow(vhost,testdir,testscript,testOutput):
    print("HANDLER: " + vhost + " " + testscript + " " + testOutput)


    #Open file and put lines in index.html file
    with open('/var/www/html/mrt2/index.html','r') as file:
        data = file.readlines()

    split = testOutput.splitlines()

    lijnGevonde = False
    pattern_for_vhost = ".?<tr>.+"+vhost+".+"
    testanchor = testdir + "\',\'" + testscript

    lineCount = 0
    fileindex = 0

    #Searched for the vhost name, when found  start counting the amount of lines equal to the check list
    # (this is to not suddenly be checking the lines from a next user)
    for line in data:
        if re.search(pattern_for_vhost, line):
            lijnGevonde = True
        if lijnGevonde == True and lineCount <= len(checks) :

            #Edits line data to represent OK
            if float(split[0]) >= 10:
                if testanchor in line:
                    data[fileindex] = re.sub(r'[HN]OK','OK',data[fileindex])
                    data[fileindex] = re.sub(r'[hn]ok.png', 'ok.png',data[fileindex])
                    data[fileindex] = re.sub(r'data-order="[0-9]"','data-order="10"', data[fileindex])
                    # print (data[fileindex])

            #Edits line data to represent HOK
            elif float(split[0]) >= 5:
                if testanchor in line:
                    data[fileindex] = re.sub(r'[NH]?OK','HOK',data[fileindex])
                    data[fileindex] = re.sub(r'[nh]?ok.png', 'hok.png',data[fileindex])
                    data[fileindex] = re.sub(r'data-order="[0-9][0-9]?"','data-order="5"', data[fileindex])
                    # print (data[fileindex])

            #Edits line data to represent NOK
            else:
                if testanchor in line:
                    data[fileindex] = re.sub(r'[HN]?OK','NOK',data[fileindex])
                    data[fileindex] = re.sub(r'[hn]?ok.png', 'nok.png',data[fileindex])
                    data[fileindex] = re.sub(r'data-order="[0-9][0-9]?"','data-order="0"', data[fileindex])


            lineCount += 1
        fileindex += 1

    #Overwrite index.html with newly assembled data file
    with open('/var/www/html/mrt2/index.html','w') as file:
        file.writelines(data)
