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
if repo_name in service_labels:
    labels.append(service_labels[repo_name])


def enhance_in_trello_card(pr_text):
    url_pattern = r'(https?://\S+)'
    links = re.findall(url_pattern, pr_text)
    cards = [card[:-1] for card in links if "trello.com" in card]

    for card in cards:
        card_id = card.split("/")[-2]
        card_labels = requests.get(f'https://api.trello.com/1/cards/{card_id}/labels',
                                   params={'key': API_KEY, 'token': API_TOKEN}).json()
        for label in card_labels:
            if label["name"] == "Enhancement":
                return True
    return False


pr_data = requests.get(f'https://api.github.com/repos/altooro/{repo_name}/pulls/{pr_number}',
                       headers={'Authorization': f'token {github_token}'}).json()

pr_name = pr_data["head"]["ref"]
pr_description = pr_data["body"]
is_label_exists = any(label["name"] == "enhancement" for label in pr_data["labels"])
card_name = f"Validate {pr_name} feature in {repo_name} service. Add automation tests if needed"
card_description = f"Validate new feature in {repo_name}\n\n**PR name:** {pr_name}\n**PR link:** " \
                   f"{pr_data['url']}\n\n---\n\n ### **PR description:**\n{pr_description}\n\n---\n\n" \
                   f"Done by: _{pr_data['user']['login']}_"

if pr_name.lower().startswith("feature/") or is_label_exists or enhance_in_trello_card(pr_description):
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
        print("Trello card created successfully.")
    else:
        print("Failed to create Trello card.")
