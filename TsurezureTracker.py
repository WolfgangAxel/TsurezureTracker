#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  TsurezureTracker.py
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

from bs4 import BeautifulSoup as BS
from requests import get,post
from re import search
from sys import argv,path
from os.path import join
from time import sleep

args = [arg for arg in argv]
myPath = __file__.replace("TsurezureTracker.py","")

def fileChecker(myPath):
    from os.path import exists
    
    if not exists(myPath+"credentials.txt"):
        exit(myPath+"credentials.txt is missing. Fix it")
    
    if not exists(join(myPath,"Archives","chapterArchive.pydic")):
        input("Chapter Archive not found. Press enter to continue.")
        with open(join(myPath,"Archives","chapterArchive.pydic"),"w") as dic:
            dic.write(str({}))
        if "--gen" not in args:
            exit("Please restart the script using the '--gen' flag")
    
    if not exists(join(myPath,"Archives","nameArchive.pydic")):
        input("Name Archive not found. Press enter to continue.")
        with open(join(myPath,"Archives","nameArchive.pydic"),"w") as dic:
            dic.write(str({}))
        exit("No Name Archive means this script does nothing. Make a new one and try again.")
    
    if not (exists(join(myPath,"Modules","Archives.py")) and exists(join(myPath,"Modules","reddit_fxns.py"))):
        exit("Necessary module(s) not found. Please go to https://github.com/WolfgangAxel/TsurezureTracker/Modules"
             " and download the missing file(s) into "+join(myPath,"Modules"))
    
    del exists

def batotoChapters(URLArray):
    """
    Takes one or more URLs to manga on Batoto and returns their chapter listings
    as a list of iterables
    """
    if type(URLArray) == str:
        URLArray = [URLArray]
    soups = []
    for series in URLArray:
        page = get(series,cookies=cookies)
        soup = BS(page.text,"html.parser")
        soups.append(soup.find_all('tr', class_="row lang_English chapter_row"))
    return soups

def getCookies(username,password):
    # Code mostly borrowed from cum
    # Great project name, btw. Go googling for that one. "Python cum"...
    url = "https://bato.to/forums/index.php"
    params = {'app': 'core', 'module': 'global','section': 'login', 'do': 'process'}
    firstGet = get(url,params=params)
    auth_key = search(r"'auth_key' value='(.+)'", firstGet.text).group(1)
    data = {'auth_key': auth_key,
            'referer': 'http://bato.to/',
            'ips_username': username,
            'ips_password': password,
            'rememberMe': 1}
    firstPost = post(url,params=params,data=data)
    cookie = firstPost.cookies['session_id']
    member_id = firstPost.cookies['member_id']
    pass_hash = firstPost.cookies['pass_hash']
    return {"cookie":cookie,"member_id":member_id,"pass_hash":pass_hash}

def printCurrentArchive():
    for character in sorted(characterLookup):
        print(character+"\n\n* Call names")
        for name in TRZRCNameCatcher[character]:
            print(" * "+name)
        print("* Chapters")
        for chapter in characterLookup[character]:
            print(" "+chapter)
        print()

fileChecker(myPath)
with open(myPath+"credentials.txt","r") as creds:
    creds = creds.read().splitlines()
R_BOT_USER = creds[0].replace("/u/","")
R_BOT_PASS = creds[1]
R_BOT_C_ID = creds[2]
R_BOT_SCRT = creds[3]
R_BOT_MAST = creds[4].replace("/u/","")
BATOTO_USR = creds[5]
BATOTO_PWD = creds[6]

TRZRCNameCatcher = eval(open(join(myPath,"Archives","nameArchive.pydic"),"r").read())
TRZRURL = "http://bato.to/comic/_/comics/tsurezure-children-r15941"
WAKAURL = "http://bato.to/comic/_/wakabayashi-toshiya%e2%80%99s-4-koma-collection-r9820"

path.append(join(myPath,"Modules"))
import Archives

cookies = getCookies(BATOTO_USR,BATOTO_PWD)

if "--gen" in args:
    while True:
        confirm = input("Generation flag detected. This will overwrite all saved data. Continue? (YES/n)\n-->")
        if confirm == "YES":
            characterLookup = Archives.buildArchive(cookies)
            break
        elif confirm == "n":
            print("Aborting")
        else:
            print("Please confirm with exactly one of the values.")
else:
    characterLookup = eval(open(join(myPath,"Archives","chapterArchive.pydic"),"r").read())

if "--md" in args:
    printCurrentArchive()

if "--add" in args:
    characters = args[args.index("--add")+1:]
    chapterURL = characters.pop(-1)
    name = characters.pop(-1)
    for character in characters:
        characterLookup = Archives.addChapter(characterLookup,character,"* ["+name.replace("[","(").replace("]",")")+"]("+chapterURL+")")
    confirm = input("Continue with bot startup? (y/n)\n-->")
    if confirm != "y":
        exit("Exiting...")

########################################################################
#     Reddit portion                                                   #
########################################################################

import reddit_fxns

reddit = reddit_fxns.startup()
print("Bot initialized successfully. Starting monitoring.")
while True:
    try:
        reddit_fxns.checkNewChaps(reddit)
        reddit_fxns.checkInbox(reddit)
        sleep(300)
    except Exception as e:
        print("Fatal error occurred:\n"+str(e.args)+"\nTrying again in 1 minute")
        sleep(60)
