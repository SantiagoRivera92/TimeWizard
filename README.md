#EDOPRO F&L list generator

This project is just a script that generates every single Time Wizard EDOPRO lflist possible.

As of 2022/02/13, there are 777 different Time Wizard formats. Every F&L and set release counts as a different format.

##I just want a banlist to use on EDOPRO

Open the lflist folder, locate the list you want (they are sorted chronologically), open it, right click on "Raw", and save it to your computer as you would save an image. Then just place it on your /repositories/lflist folder in whatever folder you installed EDOPRO in.

##I want to learn how to run the script

You need to have Python installed in order to run the script. Once you've done that, there are a number of different things the script can do depending on what parameters you pass.

The only accepted format for dates is YYYY-MM-DD. This makes it so sorting the filenames also sorts the dates chronologically. If you have an issue with using YYYY-MM-DD like a grown-up, kindly shut up about it.

> python makeBanlist.py all

This will generate every single banlist to the lflist folder. You probably don't want to use this one since it will take several hours to generate them, but I did it just so they were available to grab from the repo.

> python makeBanlist.py test

This will check whether every card in the files in the banlist folder exists. These are JSON files that I had to manually build, so I had to make sure I had written every single one correctly.

> python makeBanlist 2005-07-27

This will create the banlist for whatever date you put in the arguments. 2005-07-27 just happens to be Goat format. The filename will be 2005-07-27.lflist.conf

> python makeBanlist 2005-07-27 Goat

This will create the banlist for whatever date you put in the arguments and add the name to the filename. The filename in this case will be 2005-07-27 (Goat).lflist.conf