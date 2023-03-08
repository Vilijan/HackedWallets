import json


def load_json(path: str) -> dict:
    with open(path, encoding='utf-8') as json_file:
        data = json.load(json_file)
        return data


def save_json(file_name, json_dic):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(json_dic, f, ensure_ascii=False, indent=4)


def save_list(file_name, pydantic_list):
    json_dict = {"list": [item.dict() for item in pydantic_list]}

    save_json(file_name, json_dict)
