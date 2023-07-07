# MNEMOSYNE EXPERIMENTAL

This is a personal experimental fork of the Mnemosyne Project for feature tests and contributions to the project repository.

## Repository differences

- May break anytime. Compile and run at own risk..
- Uses semantic versioning and a rough git-flow branching structure
    + Whenever possible, this fork is synced with the master branch. Major and minor versions are bumped up upon sync.
    + Development is done in the `develop` branch. Note: `git push --all` when pushing the `master` branch.
    + all changes and releases specific to this fork are suffixed with `dev` i.e. `v2.10.1-dev`
- Uses `pyenv` for python version management, `poetry` for project management and virtual environments.
    - Due to quirks with `poetry`, `pyenv shell` is used to control which python version poetry runs. Run `pyenv shell 3.9` first before running `poetry shell`