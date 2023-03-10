import json
import time


def append_user_id_to_json(user_id):
    with open('databases/ids.json', 'r') as f:
        data = json.load(f)
    data["id"].append(user_id)
    with open('databases/ids.json', 'w') as f:
        json.dump(data, f)


for usr_id in range(100_000, 200_000):
    append_user_id_to_json(usr_id)