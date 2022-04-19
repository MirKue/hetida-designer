import pytest
import json
import os

from unittest import mock

from hetdesrun.persistence import get_db_engine, sessionmaker
from hetdesrun.persistence.dbmodels import Base
from hetdesrun.persistence.dbservice.revision import store_single_transformation_revision
from hetdesrun.persistence.models.transformation import TransformationRevision

from hetdesrun.backend.service.doctest import write_code_to_file_in_temp_dir
from hetdesrun.backend.service.doctest import execute_doctest
from hetdesrun.backend.models.info import DoctestResponse

@pytest.fixture(scope="function")
def clean_test_db_engine(use_in_memory_db):
    if use_in_memory_db:
        in_memory_database_url = "sqlite+pysqlite:///:memory:"
        engine = get_db_engine(override_db_url=in_memory_database_url)
    else:
        engine = get_db_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    return engine


@pytest.mark.asyncio
async def test_write_code_to_py_file(
    clean_test_db_engine
):
    with mock.patch(
        "hetdesrun.persistence.dbservice.revision.Session",
        sessionmaker(clean_test_db_engine),
    ):
        json_file_name = "linear-interpolation-numeric-index_100_1d53dedc-9e4a-1ccc-4dfb-3e5059f89db8.json"
        category_dir = "time-length-operations"
        with open(
            os.path.join("./transformations/components/", category_dir, json_file_name),
            encoding="utf-8"
        ) as f:
            tr_json = json.load(f)
        
        tr = TransformationRevision(**tr_json)
        store_single_transformation_revision(tr)

        temp_dir = "./tests/data/code"
        actual_path = write_code_to_file_in_temp_dir(id=tr.id, temp_dir=temp_dir)

        py_file_name = os.path.splitext(json_file_name)[0]+".py"
        py_file_path = os.path.join(temp_dir, py_file_name)
        assert actual_path == py_file_path
        assert os.path.exists(py_file_path)

        with open(py_file_path, "r") as f:
            code_from_code_file = f.read()
        assert  code_from_code_file == tr.content

        os.remove(actual_path)
        os.rmdir(temp_dir)


@pytest.mark.asyncio
async def test_execute_doctest(
    clean_test_db_engine
):
    with mock.patch(
        "hetdesrun.persistence.dbservice.revision.Session",
        sessionmaker(clean_test_db_engine),
    ):
        json_file_name = "linear-interpolation-numeric-index_100_1d53dedc-9e4a-1ccc-4dfb-3e5059f89db8.json"
        category_dir = "time-length-operations"
        with open(
            os.path.join("./transformations/components/", category_dir, json_file_name),
            encoding="utf-8"
        ) as f:
            tr_json = json.load(f)
        
        tr = TransformationRevision(**tr_json)
        store_single_transformation_revision(tr)

        temp_dir = "./tests/data/code"
        doctest_response: DoctestResponse = execute_doctest(id=tr.id, temp_dir=temp_dir)

        assert doctest_response.nof_attempted == 1
        assert doctest_response.nof_failed == 0
        assert doctest_response.output == ""

        py_file_name = os.path.splitext(json_file_name)[0]+".py"
        py_file_path = os.path.join(temp_dir, py_file_name)
        assert not os.path.exists(py_file_path)
