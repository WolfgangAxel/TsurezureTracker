#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Archives.py
#  
#  Copyright 2017 Keaton Brown <linux.keaton@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

########################################################################
#                                                                      #
#  Tsurezure Children Context Tracker                                  #
#                                                                      #
#  A reddit bot that will automatically grab all previous interactions #
#  between two characters so you can keep track of what the fuck is    #
#  going on.                                                           #
#                                                                      #
########################################################################

########################################################################
#  Functions for Archiving                                             #
########################################################################

if __name__ == '__main__':
    exit("Not a script")

import __main__

def addChapter(characterLookup,character,chapterMarkdown,botMode=False):
    """
    Adds the link markdown to the archive under a character's name
    """
    try:
        character = findNames(character)
    except:
        if botMode:
            raise Exception
        nameList = [ name for name in __main__.TRZRCNameCatcher ]
        print(character+" was not found in the list of characters. "
        "Please choose the correct name below and press enter.")
        for i,name in enumerate(nameList):
            print(str(i)+". "+name)
        print("Type 'NEW' to add a new main character.")
        while True:
            index = eval(input("-->"))
            if type(index) == int:
                character = nameList[index]
                break
            elif index == "NEW":
                character = manualAddMain()
                break
            print("Not a number or 'NEW'")
    try:
        characterLookup[character] = [ chapterMarkdown ]+characterLookup[character]
    except:
        # New character
        characterLookup[character] = [ chapterMarkdown ]
    if botMode:
        saveChapterArchive(characterLookup)
    return characterLookup

def addMain(familyName, givenName, botMode=False):
    """
    Add a main character to the archive
    """
    __main__.TRZRCNameCatcher[familyName] = [ familyName, givenName ]
    with open(__main__.join(__main__.myPath,"Archives","nameArchive.pydic"),"w") as arc:
        arc.write(str(__main__.TRZRCNameCatcher))
    if botMode:
        return "Added "+familyName+" "+givenName+" as a main character.\n\n****\n\n"

def manualAddMain():
    """
    Add a main character to the Name Catcher
    """
    while True:
        print("Please type the family name of the character:")
        familyName = input("-->")
        print("Is '"+famileName+"' correct? (y/n)")
        confirm = input("-->")
        if confirm.lower() == "y":
            familyName = familyName.capitalize()
            break
        print("Confirm failed")
    while True:
        print("Please type the given name of the character:")
        givenName = input("-->")
        print("Is '"+givenName+"' correct? (y/n)")
        confirm = input("-->")
        if confirm.lower() == "y":
            givenName = givenName.sapitalize()
            break
        print("Confirm failed")
    while True:
        print("The dictionary entry will look like this:\n"
              "'"+familyName+"':['"+familyName+"','"+givenName+"']\n"
              "Is this correct? (y/n)")
        confirm = input("-->")
        if confirm.lower() == 'y':
            addMain(familyName, givenName)
            return familyName
        elif confirm.lower() == "n":
            return manualAddMain()
        else:
            print("Confirmation failed")

def manualCharacters(name,URL):
    """
    Manually define which characters appear in a chapter
    """
    while True:
        print("No character information found in the title of "+name+".\n"+URL)
        names = input("Enter the names of all main characters involved in this chapter with spaces in between each name.\n-->")
        names = names.split(" ")
        print("You entered the following for all main characters:")
        for char in names:
            print("  "+char)
        confirm = input("Is this correct? (y/n)\n-->")
        if confirm.lower() == "y":
            break
        print("Confirmation failed. Trying again.")
    return names

def titleParse(chName):
    """
    Tries to strip the characters from a title.
    Raises Exceptions when not found, so use with try statements
    and alternative means to define characters when it fails.
    """
    try:
        characters = __main__.search(".*\((.*)\)",chName).group(1)
        if " " in characters:
            if not "love master" in characters.lower():
                # Not found, use alternate method
                raise Exception
            else:
                # Fucking LoveMaster ruining everything again.
                characters = characters.lower().replace("love master","lovemaster")
        if characters.lower() == "omake":
            # Not found, use alternate method
            raise Exception
        if characters.lower() == "tankoubon":
            # Not found, use alternate method
            raise Exception
        # Found
        characters = characters.split("/")
        return characters
    except:
        # Not found, use alternate method
        raise Exception

def findNames(character):
    """
    Returns the 'main' name for a character
    """
    for char in __main__.TRZRCNameCatcher:
        if character.lower() in [name.lower() for name in __main__.TRZRCNameCatcher[char]]:
            return char
    print("Lookup of "+character+" failed.")
    raise Exception

def findChapters(charList,characterLookup):
    """
    Pull all chapters common between a number of characters, or all
    chapters with that character in it.
    """
    # Check if a redditor sent just "CHARACTER CHARACTER...." any number of times
    if ((charList[1:] == charList[:-1]) and (charList[0] == 'character')):
        return "* You're not as funny as you think you are\n\n"
    linkString = ""
    for i,character in enumerate(charList):
        charList[i] = findNames(character)
        charList[i] = [charList[i],characterLookup[charList[i]]]
    # Remove duplicates if any
    # Honestly, I don't know exactly how this works but it does? And I wrote it myself without Googling so fuck yeah.
    testCharList = [ char for i,char in enumerate(sorted(charList)) if char != sorted(charList)[i-1] ]
    if testCharList != []:
        charList = testCharList
    else:
        # All items were removed in the test, so only one character is there.
        charList = [ charList[0] ]
    for character in [ name[0] for name in charList ]:
        linkString += character+", "
    linkString = linkString[:-2]
    if len(charList) == 1:
        linkString += " has appeared previously in:\n\n"
        for link in charList[0][1]:
            linkString += link+"\n"
    else:
        linkString += " have appeared together previously in:\n\n"
        first = charList[0][1]
        sharedLinks = []
        for links in [character[1] for character in charList[1:]][0]:
            for link in first:
                if link in links:
                    sharedLinks.append(link)
        if sharedLinks == []:
            return "* None =(\n"
        else:
            for link in sharedLinks:
                linkString += link + "\n"
    return linkString+"\n"

def buildArchive(cookies):
    """
    Generate a new chapter archive using chapters on Batoto.
    Note: This takes a looooooong time.
    """
    characterLookup={}
    for soup in __main__.batotoChapters([__main__.TRZRURL, __main__.WAKAURL]):
        for row in soup:
            chapterURL=row.td.a['href']
            columns = row.find_all('td')
            name = columns[0].img.next_sibling.strip()
            # Grab just the chapter title first,
            # then check for character names.
            # Ask for character names if not found.
            chName = __main__.search(".*: (.*)",name).group(1)
            try:
                characters = titleParse(chName)
            except:
                characters = manualCharacters(name,chapterURL)
            infoString = ""
            for character in characters:
                characterLookup = addChapter(characterLookup,character,"* ["+name.replace("[","(").replace("]",")")+"]("+chapterURL+")")
                infoString += character+", "
            print(infoString[:-2]+" appear in "+name+"\n----------")
    saveChapterArchive(characterLookup)
    return characterLookup

def saveChapterArchive(characterLookup):
    with open(__main__.join(__main__.myPath,"Archives","chapterArchive.pydic"),"w") as f:
        f.write(str(characterLookup))
