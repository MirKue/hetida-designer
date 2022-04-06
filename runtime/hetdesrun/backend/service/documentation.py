from typing import Dict, Any
from hetdesrun.datatypes import DataType
from hetdesrun.persistence.models.transformation import TransformationRevision

data_type_name: Dict[str, str] = {
    DataType.Integer: "Integer",
    DataType.Float: "Float",
    DataType.String: "String",
    DataType.DataFrame: "Pandas DataFrame",
    DataType.Series: "Pandas Series",
    DataType.Boolean: "Boolean",
    DataType.Any: "Any",
    DataType.PlotlyJson: "PlotlyJson",
}

documentation_template: str = """\
#{category}: {name} ({version_tag})

## Description
{description}

## Inputs
{inputs}

## Outputs
{outputs}

## Details


## Examples

"""


def value_to_str(value: Any, level: int = 2) -> str:

    if value is None:
        return "null"

    if isinstance(value, str):
        return '"' + value + '"'

    if isinstance(value, dict):
        value_string = (
            "{\n"
            + ("\t" * level)
            + (",\n" + ("\t" * level)).join(
                [
                    '"' + key + '": ' + value_to_str(dict_value, level=level + 1)
                    for key, dict_value in value.items()
                ]
            )
            + "\n"
            + ("\t" * (level - 1))
            + "}"
        )
        return value_string

    if isinstance(value, list):
        value_string = (
            "[\n"
            + ("\t" * level)
            + (",\n" + ("\t" * level)).join(
                [value_to_str(list_value, level=level + 1) for list_value in value]
            )
            + "\n"
            + ("\t" * (level - 1))
            + "]"
        )
        return value_string

    return str(value)


def generate_documentation(transformation_revision: TransformationRevision) -> str:
    return documentation_template.format(
        name=transformation_revision.name,
        category=transformation_revision.category,
        description=transformation_revision.description,
        version_tag=transformation_revision.version_tag,
        inputs="\n".join(
            [
                "* **" + io.name + "** (" + data_type_name[io.data_type] + "):"
                for io in transformation_revision.io_interface.inputs
                if io.name is not None
            ]
        )
        if len(transformation_revision.io_interface.inputs) > 0
        else "This component has no inputs.",
        outputs="\n".join(
            [
                "* **" + io.name + "** (" + data_type_name[io.data_type] + "):"
                for io in transformation_revision.io_interface.outputs
                if io.name is not None
            ]
        )
        if len(transformation_revision.io_interface.outputs) > 0
        else "This component has no outputs.",
    )
