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

import __main__
import praw

sub = "manga"
mySub = "TsurezureTracker"

botFlair =("Enjoy!\n\n****\n\n[^(I am a bot.)](https://github.com/WolfgangAxel/TsurezureTracker) "+
           "^(Request a lookup from me )[^(here,)](https://www.reddit.com/message/compose/?to="+__main__.R_BOT_USER+
           "&subject=Lookup&message=find%20CHARACTER%20CHARACTER%20CHARACTER%20chapters)^( or look through yourself )"+
           "[^(here.)](http://bato.to/forums/topic/23170-relationship-continuation-list-by-moredrowsy/) "+
           "^(Complaints? /r/"+mySub+")"
          )
adminCommandParsers = {
    "botHelp(parsed.group())":"help",
    "__main__.Archives.addMain(parsed.group(1).capitalize(),parsed.group(2).capitalize(),botMode = True)":"add character: (.*) as family name, (.*) as given name",
    "editChapterReply(parsed.group(1),parsed.group(2),reddit,message)":"edit submission url: (.*) characters \[(.*)\]",
    "__main__.Archives.addChapter(__main__.characterLookup,parsed.group(1),'* ['+parsed.group(2).title()+']('+parsed.group(3)+')',botMode=True)":
        "add character (.*) to chapter (.*) at url (.*)",
    "newSticky(admin=parsed.group())":"new sticky"
    }

def startup():
    """
    Make the reddit instance
    """
    try:
        return praw.Reddit(client_id=__main__.R_BOT_C_ID,
                            client_secret=__main__.R_BOT_SCRT,
                            password=__main__.R_BOT_PASS,
                            user_agent="Keeping track of Tsurezure Children chapters for /r/manga, hosted by /u/"+__main__.R_BOT_MAST,
                            username=__main__.R_BOT_USER)
    except Exception as e:
        exit("Reddit authentication failed. Check for correct credentials and internet connection\n\nMore details: "+str(e.args()))

def botHelp(_):
    """
    Return the functions and the parser for each bot command
    """
    helpText = "Here are the admin functions and parsers:\n\n"
    for command in adminCommandParsers:
        helpText += "* `"+command+"`: `"+adminCommandParsers[command]+"`\n"
    helpText += "\n****\n\n"
    return helpText

def adminFunctions(message,reddit):
    """
    Parse a PM from the botmaster with commands
    """
    greeting = "Hello, /u/"+__main__.R_BOT_MAST+"! Admin functions engaged.\n\n****\n\n"
    messageBody = ""
    for line in message.body.lower().splitlines():
        for command in adminCommandParsers:
            # Stack the output from all admin commands into one message, then
            # send it if there was any successful commands.
            try:
                parsed = __main__.search(adminCommandParsers[command],line)
                output = eval(command)
                if type(output) == str:
                    messageBody += output
                else:
                    messageBody += "Operation '"+line+"' returned non-string output, but successfully so.\n\n****\n\n"
            except Exception as e:
                if not "NoneType" in e.args[0]:
                    print("Error with "+command+"\n"+str(e.args)+"\n\n")
                continue
    if messageBody == "":
        raise Exception
    message.reply(greeting+messageBody+botFlair)

def editChapterReply(url,characters,reddit,message):
    """
    Admin function to edit the auto-response with the correct characters' chapters
    """
    greeting="Hello, /r/"+sub+"!\n\n"
    # Fucking lovemaster ruining everything
    characters = characters.replace("love master","lovemaster").split(" ")
    submission = praw.models.Submission(reddit,url=url)
    try:
        parsed = __main__.search("\[DISC\] (Wakabayashi Toshiya's 4-koma Collection|Tsurezure Children)",submission.title).group(1)
        if parsed.lower() == "tsurezure children":
            soup = __main__.batotoChapters(__main__.TRZRURL)[0]
        else:
            soup = __main__.batotoChapters(__main__.WAKAURL)[0]
        chapterURL=soup[0].td.a['href']
        columns = soup[0].find_all('td')
        name = columns[0].img.next_sibling.strip()
        chName = __main__.search(".*: (.*)",name).group(1)
    except:
        return "Incorrect submission link used.\n\n****\n\n"
    for comment in submission.comments:
        if comment.author.name.lower() == __main__.R_BOT_USER.lower():
            if "There's something I don't understand about this chapter title." in comment.body:
                try:
                    for character in characters:
                        character = __main__.Archives.findNames(character)
                        __main__.characterLookup = __main__.Archives.addChapter(__main__.characterLookup,character,"* ["+name.replace("[","(").replace("]",")")+"]("+chapterURL+")",botMode=True)
                    __main__.Archives.saveChapterArchive(__main__.characterLookup)
                    msgBody = "I've done some digging, and this is what I've found:\n\n" + __main__.Archives.findChapters(characters,__main__.characterLookup)
                except Exception as e:
                    return "Error when parsing characters:\n"+str(e.args)+"\n\n****\n\n"
                retries = 0
                while True:
                    try:
                        comment.edit(greeting+msgBody+botFlair)
                        newSticky()
                        return "Comment sucessfully edited.\n\n****\n\n"
                    except:
                        print("Comment edit failed. Internet connection error? Trying again in 30 seconds.")
                        __main__.sleep(30)
                        retries += 1
                        if retries > 60:
                            return "Failed to edit post. Internet issues? If not, IDK what happened...\n\n****\n\n"
    return "I have not commented in the thread you linked me to\n\n****\n\n"

def checkNewChaps(reddit):
    """
    Check /r/manga for a new chapter thread
    """
    for submission in reddit.subreddit(sub).new(limit=100):
        try:
            parsed = __main__.search("\[disc\] (wakabayashi toshiya's 4-koma collection|tsurezure children)",submission.title.lower()).group(1)
        except:
            continue
        if __main__.R_BOT_USER.lower() in [ comment.author.name.lower() for comment in submission.comments ]:
            # Don't comment if we've commented in that thread before
            continue
        if not "bato.to" in submission.url:
            # Gotta be Batoto, since that's where we scrape for characters
            print("Found a discussion thread, but the link wasn't Batoto.")
            continue
        print(__main__.printTime()+"----------\nFound a new chapter\n----------")
        if parsed.lower() == "tsurezure children":
            soup = __main__.batotoChapters(__main__.TRZRURL)[0]
        else:
            soup = __main__.batotoChapters(__main__.WAKAURL)[0]
        greeting="Hello, /r/"+sub+"!\n\n"
        chapterURL=soup[0].td.a['href']
        columns = soup[0].find_all('td')
        name = columns[0].img.next_sibling.strip()
        chName = __main__.search(".*: (.*)",name).group(1)
        try:
            characters = __main__.Archives.titleParse(chName)
            for character in characters:
                __main__.characterLookup = __main__.Archives.addChapter(__main__.characterLookup,character,"* ["+name.replace("[","(").replace("]",")")+"]("+chapterURL+")",botMode=True)
            __main__.Archives.saveChapterArchive(__main__.characterLookup)
            msgBody = "I've done some digging, and this is what I've found:\n\n" + __main__.Archives.findChapters(characters,__main__.characterLookup)
            print("Successful parsing. Good job, me!\nMaking new sticky...")
            newSticky()
        except:
            msgBody="There's something I don't understand about this chapter title. I've notified /u/"+__main__.R_BOT_MAST+", and once he tells me what to do, I'll edit this post with the chapters.\n\n"
            print("Error with chapter. Reply sent, should edit later")
        submission.reply(greeting+msgBody+botFlair)
        print("Reply posted")

def checkInbox(reddit):
    """
    Parse PMs and try to respond
    """
    for message in reddit.inbox.unread():
        try:
            redditor = "/u/"+message.author.name
        except:
            redditor = "/u/"+message.author
        print(__main__.printTime()+"Got a message from "+redditor)
        if redditor.lower() == "/u/"+__main__.R_BOT_MAST.lower():
            try:
                adminFunctions(message,reddit)
                message.mark_read()
                continue
            except Exception as e:
                if e.args:
                    print("Errors:\n\n"+str(e.args)+"\n\n")
                print("Admin function call failed. Proceeding with regular lookup.")
        greeting = "Hello "+redditor+"!\n\n"
        previousInteractions = ""
        try:
            request = __main__.findall("find (.*?) chapters",message.body.lower())
            if request == []:
                raise Exception
            if len(request) == 1:
                characters = request[0].replace("love master","lovemaster").split(' ')
                previousInteractions += "I've done some digging, and this is what I've found:\n\n" + __main__.Archives.findChapters(characters,__main__.characterLookup)
            else:
                fails = 0
                for req in request:
                    characters = req.replace("love master","lovemaster").split(' ')
                    try:
                        previousInteractions += "****\n\n" + __main__.Archives.findChapters(characters,__main__.characterLookup)
                    except:
                        fails += 1
                        previousInteractions += "****\n\nThere was an error with a character name in "+req.capitalize()+"\n\n"
                if fails == len(request):
                    raise Exception
                previousInteractions = "I've done some digging, and this is what I've found:\n\n" + previousInteractions[6:]
            message.reply(greeting+previousInteractions+botFlair)
            print("Message delivered successfully")
        except:
            print("Message parsing failed")
            if message.subject in ["username mention","comment reply"]:
                print("Was a mention, no message sent")
                message.mark_read()
                continue
            message.reply(greeting+"I was unable to read your message properly. "+
                          "Please check the current archive at /r/"+mySub+" for a list of acceptable names, "+
                          "and list names using only spaces in between like so:\n\n    find Gouda Kamine chapters\n\n"+botFlair)
            print("Failure notification sent")
        message.mark_read()

def newSticky(admin=False):
    """
    Generate a new archive sticky on mySub
    """
    botSub = __main__.reddit.subreddit(mySub)
    # Unset the current sticky
    try:
        stickyIndex = 1
        while True:
            stuckPost = botSub.sticky(number=stickyIndex)
            if "current archive as of " in stuckPost.title.lower():
                stuckPost.mod.remove()
                break
            stickyIndex += 1
    except:
        print("No previous sticky found. Oh well.")
    new = botSub.submit("Current Archive as of "+__main__.st("%m-%d-%y"),selftext=__main__.printCurrentArchive(botMode=True))
    new.mod.sticky(bottom=False)
    new.mod.lock()
    if admin:
        return "New sticky made successfully\n\n****\n\n"
