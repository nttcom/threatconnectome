import json
from pathlib import Path

human_impact_dict: dict = {}
ssvc_priority_dict: dict = {}


def initialize():
    if len(human_impact_dict) == 0 or len(ssvc_priority_dict) == 0:
        _create_deployer_dict()


def get_human_impact_dict() -> dict:
    if len(human_impact_dict) == 0:
        _create_deployer_dict()
    return human_impact_dict


def get_ssvc_priority_dict() -> dict:
    if len(ssvc_priority_dict) == 0:
        _create_deployer_dict()
    return ssvc_priority_dict


def _create_deployer_dict() -> None:
    try:
        deployer_file_path = Path(__file__).resolve().parent / "Deployer.json"
        with open(deployer_file_path, "r") as deployer_file:
            deployer_json = json.load(deployer_file)
            _create_human_impact_dict(deployer_json)
            _create_ssvc_priority_dict(deployer_json)
    except KeyError:
        pass


def _create_human_impact_dict(deployer_json) -> None:
    human_impact_dict.clear()
    for decision_point in deployer_json["decision_points"]:
        if decision_point["label"] == "Human Impact":
            _create_human_impact_dict_from_options(decision_point["options"])
            break


def _create_human_impact_dict_from_options(options) -> None:
    for option in options:
        human_impact_value = option["label"]
        _create_human_impact_dict_from_child_combinations(
            option["child_combinations"], human_impact_value
        )


def _create_human_impact_dict_from_child_combinations(
    child_combinations: list, human_impact_value: str
) -> None:
    for child_combination in child_combinations:
        for child_combination_data in child_combination:
            if child_combination_data["child_label"] == "Situated Safety Impact":
                safety_impacts = child_combination_data["child_option_labels"]
            if child_combination_data["child_label"] == "Mission Impact":
                mission_impacts = child_combination_data["child_option_labels"]
        for safety_impact in safety_impacts:
            for mission_impact in mission_impacts:
                human_impact_dict[(safety_impact, mission_impact)] = human_impact_value


def _create_ssvc_priority_dict(deployer_json) -> None:
    ssvc_priority_dict.clear()
    for decisions_table in deployer_json["decisions_table"]:
        key = (
            decisions_table["Exploitation"],
            decisions_table["Exposure"],
            decisions_table["Automatable"],
            decisions_table["Human Impact"],
        )
        ssvc_priority_dict[key] = decisions_table["Priority"]
