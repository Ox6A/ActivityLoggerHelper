Activity Logger Helper
====================
A Discord bot written in Python for the Garry's Mod server Riverside Roleplay, aimed at allowing easy tallying of Higher Up activity in the various subdepartments.

Installing
-----------

**Python 3.8 or higher is required**

.. code:: sh

    # Windows
    py -m pip install -U discord-py
    git clone https://github.com/Ox6A/ActivityLoggerHelper
    cd ActivityLoggerHelper
    py index.py

    # If you need to install Python, open Powershell and run:
    winget install python.python.3.12

    # Linux/macOS
    python3 -m pip install -U discord-py
    git clone https://github.com/Ox6A/ActivityLoggerHelper
    cd ActivityLoggerHelper
    python3 index.py

    #If you need to install Python:
    sudo apt-get install python3 python3-pip
    sudo dnf install python3 python3-pip
    sudo pacman -Syu python3 python3-pip

Notes
-----
- Follow this guide to setup your bot: https://discordpy.readthedocs.io/en/stable/discord.html
- You do not require ``discord-py[voice]``.
- You must place your Bot's token in a ``token.txt`` file, located in the same directory as the script. (``ActivityLoggerHelper``)

Links
------
- `discord.py <https://discordpy.readthedocs.io/en/stable/>`_
- `Riverside Roleplay <https://rsrp.uk/>`_
