import json
from pathlib import Path

"""
Get Deployer.json from the repository below and extract the calculation logic from it.
https://github.com/CERTCC/SSVC

In threatconnectome, the following modifications were made to Deployer.json.

1.
  Change the Safety Impact selection from v1.0.0 to v2.0.0
2.
  Mission Impact v2.0.0 does not have None, so exclude the case where Mission Impact is None.
3.
  The following standards do not define a case where Safety Impact is Critical and Mission Impact
  is MEF Failure.
  https://certcc.github.io/SSVC/reference/decision_points/human_impact/
  Human Impact v2.0.1

  At threatconnectome, the Human Impact in this case is rated High.
  Reason:
  a.
    The value of v1.0.0 that corresponds to "Critical" in Safety Impact v2.0.0 is "Hazardous".
  b.
    In the example below, the Human Impact is set to High for cases where Situated Safety Impact
    is hazardous and Mission Impact is mef failure.
"""

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
