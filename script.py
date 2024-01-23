import requests
import os
import re


github_token = os.environ["GITHUB_TOKEN"]
API_KEY = os.environ["TRELLO_API_KEY"]
API_TOKEN = os.environ["TRELLO_TOKEN"]
board_id = os.environ["BOARD_ID"]
list_id = os.environ["LIST_ID"]
pr_number = os.environ["PR_NUMBER"]
repo_name = os.environ["REPO_NAME"]

service_labels = {"frontend-v2": "612f2ddde2df04548ffd4d8f", "journeys": "611f7b5f2cdc59646f4c6fab",
                  "data-analytics-svc": "6167db710980fd6e4cacae35", "dashboard-svc": "645e00d4e45c525971574b7f",
                  "challenges": "6128edd1aab6e98f3ba9f8b7"}
labels = ["6106563eccf9157bc07a8b46"] #Task label

# qa_priority_board: index = 0 is the highest, index = 0 is the lowest
qa_priority_board = ["61e6c2254b3908441f90fe9d", "61e6c2254b3908441f90fe9e", "61e6c2254b3908441f90fe9f",
                     "61e6c2254b3908441f90fea0", "61e6c2254b3908441f90fea1", "61e6c2254b3908441f90fea2"]
priority_field_id = "61e6c2254b3908441f90fe9b"
if repo_name in service_labels:
    labels.append(service_labels[repo_name])


def bug_not_in_trello_card(pr_text):
    create_card = True
    if pr_text:
        url_pattern = r'(https?://\S+)'
        links = re.findall(url_pattern, pr_text)
        cards = [card[:-1] for card in links if "trello.com" in card]

        for card in cards:
            card_id = card.split("/")[-2]
            card_labels = requests.get(f'https://api.trello.com/1/cards/{card_id}/labels',
                                       params={'key': API_KEY, 'token': API_TOKEN}).json()
            for label in card_labels:
                if label["name"] == "Bug":
                    create_card = False
                    break
    return create_card


def get_priorities_list(card_id):
    board_priority = requests.get(f'https://api.trello.com/1/cards/{card_id}/customFields',
                                  params={'key': API_KEY, 'token': API_TOKEN}).json()[0]["options"]
    priorities_list = []
    for priority in board_priority:
        priorities_list.append(priority['id'])
    return priorities_list


def get_card_priority(pr_text):
    the_highest_priority_index = 9
    try:
        if pr_text:
            url_pattern = r'(https?://\S+)'
            links = re.findall(url_pattern, pr_text)
            cards = [card[:-1] for card in links if "trello.com" in card]
            for card in cards:
                card_id = card.split("/")[-2]
                board_priority_list = get_priorities_list(card_id)
                card_priority = requests.get(f'https://api.trello.com/1/cards/{card_id}/customFieldItems',
                                             params={'key': API_KEY, 'token': API_TOKEN}).json()
                if card_priority:
                    if the_highest_priority_index > board_priority_list.index(card_priority[0]["idValue"]):
                        the_highest_priority_index = board_priority_list.index(card_priority[0]["idValue"])
    except:
        pass  # When something goes wrong with the priority, ensure the code doesn't crash
    return the_highest_priority_index


pr_data = requests.get(f'https://api.github.com/repos/altooro/{repo_name}/pulls/{pr_number}',
                       headers={'Authorization': f'token {github_token}'}).json()

pr_name = pr_data["head"]["ref"]
pr_description = pr_data["body"]
card_name = f"Validate {pr_name} feature in {repo_name} service. Add automation tests if needed"
card_description = f"Validate new feature in {repo_name}\n\n**PR name:** {pr_name}\n**PR link:** " \
                   f"{pr_data['html_url']}\n\n---\n\n ### **PR description:**\n{pr_description}\n\n---\n\n" \
                   f"Done by: _{pr_data['user']['login']}_"

if pr_name.lower().startswith("feature/") and bug_not_in_trello_card(pr_description):
    priority_index = get_card_priority(pr_description)
    query = {
        "key": API_KEY,
        "token": API_TOKEN,
        "idList": list_id,
        "name": card_name,
        "desc": card_description,
        "idLabels": labels
    }
    response = requests.post("https://api.trello.com/1/cards", params=query)
    if response.status_code == 200:
        created_card_id = response.json()["id"]
        if priority_index <= len(qa_priority_board):
            custom_field_payload = {"idValue": qa_priority_board[priority_index]}
            requests.put(f'https://api.trello.com/1/cards/{created_card_id}/customField/{priority_field_id}/item',
                         data=custom_field_payload, params={"key": API_KEY, "token": API_TOKEN})
    else:
        print("Failed to create Trello card.")
