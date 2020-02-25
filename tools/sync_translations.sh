#! /bin/bash
# Translation background:
#   po files: contain the actual translations.
#   pot file: contains the strings that need to be translated.
# How does it work?
# We commit pot file updates to a Launchpad repository:
#   ~mnemosyne-proj/translations
# Users can translate this pot file through the 'translations' interface.
# Launchpad exports the translated files (the po files) to another repository:
#   ~jmehne/mnemosyne-proj/po-translations
# We pull these po files and commit them to a Github repository:
#   mnemosynebot/mnemosyne (translation branch)
# Then, from time to time, someone has to manually merge the
# mnemosynebot/mnemosyne/translation branch into mnemosyne-proj/mnemosyne
# master.
#
# For this to work without manual intervention, authentication needs to be
# set up properly. Edit your ~/.ssh/config file and add the following two
# entries. Make sure that the `IdentityFile` lines point to the correct
# private key files.
#
# Host github.com-mnemosynebot
#     HostName github.com
#     User git
#     IdentityFile ~/.ssh/<private-key>
#
# Host bazaar.launchpad.net
# User <launchpad-username>
# IdentityFile ~/.ssh/<launchpad-private-key>

BZR_PO_DIR="bzr-po"
BZR_POT_DIR="bzr-pot"
GIT_BASE_DIR="mnemosynebot"
GIT_DIR="${GIT_BASE_DIR}/.git"

exitfunc()
{
    echo "$1"
    exit 1
}

if [ ! -d ${GIT_DIR} ]; then
    echo "!Cloning mnemosynebot git repository from Github."
    git clone https://github.com/mnemosynebot/mnemosyne ${GIT_BASE_DIR}
    if [ $? -ne 0 ]; then exitfunc "Could not clone mnemosynebot repo."; fi
    git --git-dir="${GIT_DIR}" --work-tree="${GIT_BASE_DIR}" remote add upstream https://github.com/mnemosyne-proj/mnemosyne
    if [ $? -ne 0 ]; then exitfunc "Could not add remote to repo."; fi
    git --git-dir="${GIT_DIR}" --work-tree="${GIT_BASE_DIR}" remote remove origin
    if [ $? -ne 0 ]; then exitfunc "Could not remove 'origin' remote."; fi
    # We use github.com-mnemosynebot as url here - this must match the string
    # used in ~/.ssh/config (see initial docstring).
    git --git-dir="${GIT_DIR}" --work-tree="${GIT_BASE_DIR}" remote add origin git@github.com-mnemosynebot:mnemosynebot/mnemosyne.git
    if [ $? -ne 0 ]; then exitfunc "Could not add ssh origin remote."; fi
fi

if [ ! -d ${BZR_PO_DIR} ]; then
    echo "!Cloning bzr po repository (repo that Launchpad exports po updates to)."
    bzr branch lp:~jmehne/mnemosyne-proj/po-translations ${BZR_PO_DIR}
    if [ $? -ne 0 ]; then exitfunc "Could not clone Launchpad po repo."; fi
fi

if [ ! -d ${BZR_POT_DIR} ]; then
    echo "!Cloning bzr pot repository (used to push pot updates from git.)"
    bzr branch lp:mnemosyne-proj/translations ${BZR_POT_DIR}
    if [ $? -ne 0 ]; then exitfunc "Could not clone Launchpad pot repo."; fi
fi

echo "!Fetching new pot file from git master."
git --git-dir=${GIT_DIR} --work-tree=${GIT_BASE_DIR} checkout master
if [ $? -ne 0 ]; then exitfunc "Could not checkout git repo."; fi
git --git-dir=${GIT_DIR} --work-tree=${GIT_BASE_DIR} pull upstream master
if [ $? -ne 0 ]; then exitfunc "Could not pull from upstream git repo."; fi
echo "!Pulling pot bzr dir, just to be sure."
(cd ${BZR_POT_DIR} && bzr pull :parent)
if [ $? -ne 0 ]; then exitfunc "Could not pull from pot bzr repo."; fi
cp "${GIT_BASE_DIR}/po/mnemosyne.pot" "${BZR_POT_DIR}"
if [ $? -ne 0 ]; then exitfunc "Could not copy pot file to bzr dir."; fi

echo "!Committing mnemosyne.pot to bzr."
(cd ${BZR_POT_DIR} && bzr commit --message "Automatic translation update.")
if [ $? -ne 0 ]; then exitfunc "Could not commit pot file to bzr repo or no changes to be committed."; fi
echo "!Pushing pot file to bzr/launchpad."
(cd ${BZR_POT_DIR} && bzr push :parent)
if [ $? -ne 0 ]; then exitfunc "Could not push pot file to bzr repo."; fi

# Fetch exported po translations from Launchpad
echo "!Pulling new po translations from Launchpad."
(cd ${BZR_PO_DIR} && bzr pull)
if [ $? -ne 0 ]; then exitfunc "Could not pull po files from bzr repo."; fi
echo "!Committing new po files to git - checking out translations branch."
# Make sure that the translations branch exists.
git --git-dir=${GIT_DIR} --work-tree="${GIT_BASE_DIR}" fetch origin
if [ $? -ne 0 ]; then exitfunc "Could fetch git repository."; fi
git --git-dir=${GIT_DIR} --work-tree="${GIT_BASE_DIR}" checkout translations
if [ $? -ne 0 ]; then exitfunc "Could not check out translation branch."; fi
cp ${BZR_PO_DIR}/*.po "${GIT_BASE_DIR}/po"
if [ $? -ne 0 ]; then exitfunc "Could not copy po files to git repo."; fi
git --git-dir=${GIT_DIR} --work-tree="${GIT_BASE_DIR}" add "po/*.po"
if [ $? -ne 0 ]; then exitfunc "Could not add new po files to git repo."; fi
git --git-dir="${GIT_DIR}" --work-tree="${GIT_BASE_DIR}" commit -m "Updated Launchpad translations."
if [ $? -ne 0 ]; then exitfunc "Could not commit po files to git repo."; fi
echo "!Pushing new po files to git."
git --git-dir="${GIT_DIR}" --work-tree="{$GIT_BASE_DIR}" push origin translations
if [ $? -ne 0 ]; then exitfunc "Could not push git repo."; fi
