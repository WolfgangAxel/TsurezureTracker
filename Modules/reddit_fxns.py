#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  reddit_fxns.py
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

from __main__ import R_BOT_USER, R_BOT_PASS, R_BOT_C_ID, R_BOT_SCRT, R_BOT_MAST, BATOTO_USR, BATOTO_PWD, characterLookup, Archives, batotoChapters, get, search, TRZRURL, WAKAURL
import praw

sub = "manga"
mySub = "TsurezureTracker"

botFlair = "Enjoy!\n\n****\n\n[^(I am a bot.)](https://github.com/WolfgangAxel/TsurezureTracker) [^(Request a lookup here.)](https://www.reddit.com/message/compose/?to=TsurezureTracker&subject=Lookup&message=find%20CHARACTER%20CHARACTER%20CHARACTER%20chapters) ^(Complaints? /r/"+mySub+")"

def startup():
    try:
        return praw.Reddit(client_id=R_BOT_C_ID,
                            client_secret=R_BOT_SCRT,
                            password=R_BOT_PASS,
                            user_agent="Keeping track of Tsurezure Children chapters for /r/manga, hosted by /u/"+R_BOT_MAST,
                            username=R_BOT_USER)
    except Exception as e:
        exit("Reddit authentication failed. Check for correct credentials and internet connection\n\nMore details: "+str(e.args()))

def checkNewChaps(reddit):
    """
    Check /r/manga for a new chapter thread
    """
    for submission in reddit.subreddit(sub).new(limit=100):
        try:
            parsed = search("\[DISC\] (Wakabayashi Toshiya's 4-koma Collection|Tsurezure Children)",submission.title).group(1)
        except:
            continue
        if R_BOT_USER.lower() in [ comment.author.name.lower() for comment in submission.comments ]:
            # Don't comment if we've commented in that thread before
            continue
        if not "bato.to" in submission.url:
            # Gotta be Batoto, since that's where we scrape for characters
            print("Found a discussion thread, but the link wasn't Batoto.")
            continue
        print("----------\nFound a new chapter\n----------")
        if parsed.lower() == "tsurezure children":
            soup = batotoChapters(TRZRURL)[0]
        else:
            soup = batotoChapters(WAKAURL)[0]
        chapterURL=soup[0].td.a['href']
        columns = soup[0].find_all('td')
        name = columns[0].img.next_sibling.strip()
        chName = search(".*: (.*)",name).group(1)
        try:
            characters = Archives.titleParse(chName)
            for character in characters:
                characterLookup = addChapter(characterLookup,character,"* ["+name.replace("[","(").replace("]",")")+"]("+chapterURL+")",botMode=True)
            Archives.saveChapterArchive(characterLookup)
            previousInteractions = "I've done some digging, and this is what I've found:\n\n" + Archives.findChapters(characters,characterLookup)
        except:
            msg="There's a new chapter of "+parsed+", but the title parse failed. [Check to see if I need to be called to the thread.]("+submission.shortlink+")"
            reddit.redditor(R_BOT_MAST).message("Failed to find characters",msg)
            print("Error with chapter. Message sent")
            continue
        submission.reply("Hello, /r/"+sub+"!\n\n"+previousInteractions+botFlair)
        print("Successful reply. Good job, me!")

def checkInbox(reddit):
    for message in reddit.inbox.unread():
        try:
            redditor = "/u/"+message.author.name
        except:
            redditor = "/u/"+message.author
        print("Got a message from "+redditor)
        greeting = "Hello "+redditor+"!\n\n"
        message.mark_read()
        try:
            parser = "find (.*) chapters"
            if message.subject == "username mention":
                parser = "u/"+R_BOT_USER+" "+parser
            characters = search(parser.lower(),message.body.lower()).group(1).split(' ')
            previousInteractions = "I've done some digging, and this is what I've found:\n\n" + Archives.findChapters(characters,characterLookup)
            message.reply(greeting+previousInteractions+botFlair)
            print("Message delivered successfully")
        except:
            print("Message parsing failed")
            if message.subject == "username mention":
                print("Was a mention, no message sent")
                continue
            message.reply(greeting+"I was unable to read your message properly. "+
                          "Please check the current archive at /r/"+mySub+" for a list of acceptable names, "+
                          "and list names using only spaces in between like so:\n\n    find Gouda Kamine chapters"+botFlair)
            print("Failure notification sent")
