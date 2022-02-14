# EDOPRO F&L list generator

This project is just a script that generates every single Time Wizard EDOPRO lflist possible.

## I just want a banlist to use on EDOPRO

Open the lflist folder, locate the list you want (they are sorted chronologically, and there's a 99% chance the one you want is in the curated folder), open it, right click on "Raw", and save it to your computer as you would save an image. Then just place it on your /repositories/lflist folder in whatever folder you installed EDOPRO in.

## I want to learn how to run the script

You need to have Python installed in order to run the script. Once you've done that, there are a number of different things the script can do depending on what parameters you pass.

The only accepted format for dates is YYYY-MM-DD. This makes it so sorting the filenames also sorts the dates chronologically. If you have an issue with using YYYY-MM-DD like a grown-up, kindly shut up about it.

If you're trying to run the script on Windows, you need to type "py" instead of "python" in CMD (unless you're using a clone of Bash as your console, in which case you have run a python script before and you don't need me to explain)

> python makeBanlist.py all

This will generate every single banlist to the lflist folder.

> python makeBanlist.py popular

This will generate all the popular retro formats.

> python makeBanlist.py test

This will check whether every card in the files in the banlist folder exists. These are JSON files that I had to manually build, so I had to make sure I had written every single one correctly.

> python makeBanlist 2005-07-27

This will create the banlist for whatever date you put in the arguments. 2005-07-27 just happens to be Goat format. The filename will be 2005-07-27.lflist.conf

> python makeBanlist 2005-07-27 Goat

This will create the banlist for whatever date you put in the arguments and add the name to the filename. The filename in this case will be 2005-07-27 (Goat).lflist.conf

### Special thanks to [Larikk](https://github.com/Larikk) for telling me over 15 errors I had in my banlists. Absolute GOAT.
