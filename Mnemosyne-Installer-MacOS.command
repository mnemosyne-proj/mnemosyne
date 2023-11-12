#!/bin/bash

# This installer pulls mnemosyne from the pip registry. It requires that you have Python installed via https://www.python.org/downloads/macos

# make sure python is installed properly and accessible
/Applications/Python*/Update\ Shell\ Profile.command

# create some helpful launchers on the Desktop
echo << EOF > /Applications/Mnemosyne.command
mnemosyne
EOF
echo << EOF > /Applications/Mnemosyne-updater.command
pip3 install --upgrade mnemosyne-proj
EOF
chmod +x ~/Mnemosyne.command /Applications/Mnemosyne-updater.command

/Applications/Mnemosyne-updater.command # the actual install happens via this command