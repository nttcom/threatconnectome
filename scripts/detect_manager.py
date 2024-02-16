# input: trivy-image-django-cdx.json
# output: package-magager.json

import json
import sys

from cyclonedx.exception import MissingOptionalDependencyException
from cyclonedx.model import Property
from cyclonedx.model.bom import Bom
from cyclonedx.schema import SchemaVersion
from cyclonedx.validation.json import JsonStrictValidator
from sortedcontainers import SortedSet


def load_text(filename) -> str:
    with open(filename) as f:
        jtext = f.read()

    if not jtext:
        print(
            "The JSON data does not exist.",
            file=sys.stderr,
        )
        sys.exit(1)
    return jtext


def is_validate_cyclonedx(jtext: str) -> bool:
    my_json_validator = JsonStrictValidator(SchemaVersion.V1_5)
    try:
        # Check CycloneDX v1.5 format
        validation_errors = my_json_validator.validate_str(jtext)
        if validation_errors:
            print(
                "Error: CycloneDX v1.5 JSON invalid: ",
                repr(validation_errors),
                file=sys.stderr,
            )
            return False
    # 'json-validation' is not installed
    except MissingOptionalDependencyException:
        print(
            "Error: Missing 'json-validation' extras.",
            'Run `pip install "cyclonedx-python-lib[json-validation]"`',
            file=sys.stderr,
        )
        return False
    return True


def load_cyclonedx(filename) -> Bom:
    with open(filename) as input_json:
        json_data = json.loads(input_json.read())
    try:
        deserialized_bom = Bom.from_json(data=json_data)
    except AttributeError:
        json_data["metadata"]["tools"] = []
        deserialized_bom = Bom.from_json(data=json_data)
    return deserialized_bom


def get_sbom_generator_name(deserialized_bom: Bom) -> str:
    tools = deserialized_bom.metadata.tools
    # tool名を削除した場合、デフォルト値は"cyclonedx-python-lib"
    if len(tools) > 0 and tools[0].name != "cyclonedx-python-lib":
        return tools[0].name

    # HACK: コンポーネントのプロパティ名から、tool名を取得
    tool_name = tool_name_from_component_property(deserialized_bom)

    # toolsが"cyclonedx-python-lib"または""のとき、コンポーネントのプロパティを確認
    return tool_name


def tool_name_from_component_property(deserialized_bom: Bom) -> str:
    property_names = set()
    for c in deserialized_bom.components:
        for p in c.properties:
            if p.name:
                property_names.add(p.name)

    tool_metadata = {"aquasecurity:trivy:PkgType": "trivy", "syft:package:metadataType": "syft"}

    # tool名を取得
    for k in tool_metadata:
        if k in property_names:
            return tool_metadata[k]

    return ""


def detect_package_managers(components: SortedSet, tool: str):
    package_managers = {}
    for c in components:
        if tool == "trivy":
            package_managers[str(c.bom_ref)] = trivy_package_manager(c.properties)
        elif tool == "syft":
            package_managers[str(c.bom_ref)] = syft_package_manager(c.properties)
        else:
            # サポートしていないツールの場合は、パッケージマネージャの情報を空に
            package_managers[str(c.bom_ref)] = ""
    return package_managers


def trivy_package_manager(properties: SortedSet[Property]) -> str:
    for p in properties:
        if p.name == "aquasecurity:trivy:PkgType":
            return p.value
    return ""


def syft_package_manager(properties: SortedSet[Property]) -> str:
    # TODO: 対応表を書く
    rename_pairs = {
        "apk-db-entry": "alpine",
        "python-package": "python-pkg",
        "javascript-npm-package-lock-entry": "npm",
        "python-pipfile-lock-entry": "pipenv",
    }
    for p in properties:
        if p.name == "syft:package:metadataType":
            if p.value in rename_pairs.keys():
                return rename_pairs[p.value]
            return ""
    return ""


def save_bom_ref_info(package_managers: dict, fname: str):
    with open(fname, "w") as f:
        json.dump(package_managers, f, indent=2)


def main():
    filename = "syft-file-tc-cdx.json"

    # 対象のファイルがCycloneDX v1.5か確認する
    jtext = load_text(filename)
    if not is_validate_cyclonedx(jtext):
        sys.exit(1)

    # CycloneDX v1.5のファイルを読み込む
    deserialized_bom = load_cyclonedx(filename)

    # tool名の検出
    tool = get_sbom_generator_name(deserialized_bom)
    if tool in ["trivy", "syft"]:

        # SBOM作成ツール固有のパッケージマネージャ情報を取得
        package_managers = detect_package_managers(deserialized_bom.components, tool=tool)

        # bom_refとパッケージマネージャのペアを保存
        save_bom_ref_info(package_managers, "package-manager.json")
    else:
        print("The SBOM Generator is not supported:", tool)


if __name__ == "__main__":
    main()
