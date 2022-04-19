import os
import io
import json
import doctest

from contextlib import redirect_stdout

from uuid import UUID

from hetdesrun.utils import Type

from hetdesrun.persistence.dbservice.revision import read_single_transformation_revision

from hetdesrun.exportimport.export import generate_file_name
from hetdesrun.backend.models.info import DoctestResponse


def write_code_to_file_in_temp_dir(
    # pylint: disable=redefined-builtin
    id: UUID,
    temp_dir: str = "./transformations/code/",
) -> str:
    os.makedirs(temp_dir, exist_ok=True)
    transformation_revision = read_single_transformation_revision(id)
    file_name = generate_file_name(transformation_revision.dict(), ".py")

    if transformation_revision.type != Type.COMPONENT:
        raise Exception(
            (
                "Transformation revision %s is of type 'WORKFLOW',"
                " thus code cannot be written to a file",
                id,
            )
        )
    assert isinstance(transformation_revision.content, str)  # hint for mypy

    code_file_path = os.path.join(temp_dir, file_name + ".py")
    with open(code_file_path, "w", encoding="utf8") as f:
        f.write(transformation_revision.content)

    return code_file_path


def execute_doctest(
    # pylint: disable=redefined-builtin
    id: UUID,
    temp_dir: str = "./transformations/code/",
) -> DoctestResponse:
    code_file_path = write_code_to_file_in_temp_dir(id, temp_dir)
    with io.StringIO() as buffer, redirect_stdout(buffer):
        test_result = doctest.testfile(code_file_path, module_relative=False)
        output = buffer.getvalue()
    return DoctestResponse(
        nof_failed=test_result.failed,
        nof_attempted=test_result.attempted,
        output=output,
    )


def write_all_code_files(source_path: str, temp_dir: str) -> None:
    os.makedirs(temp_dir, exist_ok=True)
    for root, _, files in os.walk(source_path):
        for file in files:
            current_path = os.path.join(root, file)
            if current_path.endswith("json"):
                with open(current_path, "r", encoding="utf-8") as f:
                    transformation_revision = json.load(f)
                if transformation_revision["type"] == Type.COMPONENT:
                    code_file = os.path.join(temp_dir, file.split(".")[0] + ".py")
                    with open(code_file, "w", encoding="utf8") as f:
                        f.write(transformation_revision["content"])
