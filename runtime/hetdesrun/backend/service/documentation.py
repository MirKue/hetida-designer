from typing import Dict
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
    DataType.PlotlyJson: "PlotlyJson"
}

documentation_template: str = """\
# {name} ({category})

## Description
{description}

## Inputs
{inputs}

## Outputs
{outputs}

## Details

"""

def generate_documentation(transformation_revision: TransformationRevision) -> str:
    return documentation_template.format(
        inputs=
        "".join(
            [
                "* **" + io.name + " (" + data_type_name[io.data_type] + "):\n"
                for io in transformation_revision.io_interface.inputs if io.name is not None
            ]
        ),
        outputs=
        "".join(
            [
                "* **" + io.name + " (" + data_type_name[io.data_type] + "):\n"
                for io in transformation_revision.io_interface.outputs if io.name is not None
            ]
        ),
        name=transformation_revision.name,
        category=transformation_revision.category,
        description=transformation_revision.description,
    )
