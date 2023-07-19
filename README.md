# create-trello-card

This repository contains a script that automatically creates Trello cards in a specific board and list based on certain conditions related to pull requests.


### Script Functionality

The script (`script.py`) is designed to create Trello cards based on the following conditions:

1. **PR Name Starts with `feature/`**:
   - If a pull request is opened, and its name starts with `feature/`, the script will create a Trello card with the same name in the designated Trello board and list.

2. **PR has the Label `enhancement`**:
   - If a pull request is opened and it has the label `enhancement`, the script will create a Trello card with the PR title in the designated Trello board and list.

3. **Trello Card Mentioned in PR Description has `Enhancement` Label**:
   - If a pull request is opened and it mentions a Trello card in its description, the script will check if the mentioned Trello card has the label `Enhancement`. If it does, the script will create a Trello card with the PR title in the designated Trello board and list.
