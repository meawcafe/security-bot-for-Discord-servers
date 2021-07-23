# this is a simple example of a security bot for Discord servers

**what does the bot do?**
- prevents **raid**, **flood** and **invitation from external servers** 

**how does automatic punishment work?**
- the bot will detect any behavior that fits with raid, flood or sending invitations to the server and will warn the member not to repeat it. If the member performs the same action after the warning, the bot will automatically mute the member for 5 minutes
- the bot actions will be logged
- the bot has extra security to avoid problems with the silenced members (in case Discord becomes slow or other platform issues, the bot will be prepared to resolve all issues when everything normalizes)
- there are also other moderation commands, such as a purge and a lock channel

you need to configure the bot for it to work on your server. See the config.json file

fork the repository and change the code according to your needs

see requirements in the requirements.txt file

> python version == 3.9.6

> discord.py == 1.7.3

i am a beginner programmer. I still have a lot to learn