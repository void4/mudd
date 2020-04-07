## mudd - Multi User Discord Dungeon

### Installation

#### Install Git (to get updated versions of the bot later)

- Linux: `sudo apt install git`
- Windows: https://gitforwindows.org/

#### Install Python

https://www.python.org/ -> Downloads -> Python 3.8.2

When installing on Windows, check "Add to PATH"

On Linux I'd recommend using [pyenv](https://github.com/pyenv/pyenv)

#### Download this repository

`git clone https://github.com/void4/mudd.git`

#### Discord Bot creation

https://discordapp.com/developers/applications

Add an application

Bot -> Add a Bot

Go to OAuth2

In the first set of fields, check *bot*

In the second set of fields, check *Sending Messages*

Copy the URL from the middle, open it in a new browser tab and add the bot to your server.

#### Python Bot installation and configuration

Go into the repository folder with cd ('change directory')

`cd mudd`

Install the required Python libraries

`pip install -r requirements.txt`

Copy example-config.ini to config.ini

On the Discord Bot page:

Reveal token

Paste it into config.ini's DISCORDTOKEN field

Set your own Discord username in the WIZARDS field (this allows you to make players wizards using the bot, but doesn't make yourself one yet)

### Run the bot

Now that the server is running, start the bot with

`python bot.py`

Your bot should now be online on your server

Use `python bot.py --help` to see advanced options.

#### Ingame commands

See [USAGE.md](USAGE.md)

### Notes

For more information see here:

Related:
https://www.reddit.com/r/MUD/comments/fsf59a/discord_lambdamoo_experiment/
