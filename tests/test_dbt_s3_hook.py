import pytest

try:
    from airflow_dbt_python.hooks.dbt_s3 import DbtS3Hook
except ImportError:
    pytest.skip(
        "S3Hook not available, consider installing amazon extras",
        allow_module_level=True,
    )


def test_get_dbt_profiles(s3_bucket, tmpdir, profiles_file):
    """Test pulling dbt profile from S3 path"""
    hook = DbtS3Hook()
    bucket = hook.get_bucket(s3_bucket)

    with open(profiles_file) as pf:
        profiles_content = pf.read()
    bucket.put_object(Key="profiles/profiles.yml", Body=profiles_content.encode())

    profiles_path = hook.get_dbt_profiles(
        f"s3://{s3_bucket}/profiles/",
        profiles_dir=str(tmpdir),
    )

    assert profiles_path.exists()

    with open(profiles_path) as f:
        result = f.read()
    assert result == profiles_content


def test_get_dbt_profiles_sub_dir(s3_bucket, tmpdir, profiles_file):
    hook = DbtS3Hook()
    bucket = hook.get_bucket(s3_bucket)

    with open(profiles_file) as pf:
        profiles_content = pf.read()
    bucket.put_object(
        Key="profiles/v0.0.1/profiles.yml", Body=profiles_content.encode()
    )

    profiles_path = hook.get_dbt_profiles(
        f"s3://{s3_bucket}/profiles/v0.0.1",
        profiles_dir=str(tmpdir),
    )

    assert profiles_path.exists()

    with open(profiles_path) as f:
        result = f.read()
    assert result == profiles_content


def test_get_dbt_profiles_sub_dir_trailing_slash(s3_bucket, tmpdir, profiles_file):
    """
    Test whether an S3 path without a trailing slash successfully pulls a dbt project
    """
    hook = DbtS3Hook()
    bucket = hook.get_bucket(s3_bucket)

    with open(profiles_file) as pf:
        profiles_content = pf.read()
    bucket.put_object(
        Key="profiles/v0.0.1/profiles.yml", Body=profiles_content.encode()
    )

    profiles_path = hook.get_dbt_profiles(
        f"s3://{s3_bucket}/profiles/v0.0.1/",
        profiles_dir=str(tmpdir),
    )

    assert profiles_path.exists()

    with open(profiles_path) as f:
        result = f.read()
    assert result == profiles_content


def test_get_dbt_project(s3_bucket, tmpdir, dbt_project_file):
    """Test pulling dbt project from S3 path"""
    hook = DbtS3Hook()
    bucket = hook.get_bucket(s3_bucket)

    with open(dbt_project_file) as pf:
        project_content = pf.read()
    bucket.put_object(Key="project/dbt_project.yml", Body=project_content.encode())
    bucket.put_object(Key="project/models/a_model.sql", Body=b"SELECT 1")
    bucket.put_object(Key="project/models/another_model.sql", Body=b"SELECT 2")
    bucket.put_object(Key="project/data/a_seed.csv", Body=b"col1,col2\n1,2")

    project_path = hook.get_dbt_project(
        f"s3://{s3_bucket}/project/",
        project_dir=str(tmpdir),
    )

    assert project_path.exists()

    dir_contents = [f for f in project_path.iterdir()]
    assert sorted(str(f.name) for f in dir_contents) == [
        "data",
        "dbt_project.yml",
        "models",
    ]

    with open(project_path / "dbt_project.yml") as f:
        result = f.read()
    assert result == project_content

    with open(project_path / "models" / "a_model.sql") as f:
        result = f.read()
    assert result == "SELECT 1"

    with open(project_path / "models" / "another_model.sql") as f:
        result = f.read()
    assert result == "SELECT 2"

    with open(project_path / "data" / "a_seed.csv") as f:
        result = f.read()
    assert result == "col1,col2\n1,2"


def test_get_dbt_project_no_trailing_slash(s3_bucket, tmpdir, dbt_project_file):
    """
    Test whether an S3 path without a trailing slash successfully pulls a dbt project
    """
    hook = DbtS3Hook()
    bucket = hook.get_bucket(s3_bucket)

    with open(dbt_project_file) as pf:
        project_content = pf.read()
    bucket.put_object(Key="project/dbt_project.yml", Body=project_content.encode())
    bucket.put_object(Key="project/models/a_model.sql", Body=b"SELECT 1")
    bucket.put_object(Key="project/models/another_model.sql", Body=b"SELECT 2")
    bucket.put_object(Key="project/data/a_seed.csv", Body=b"col1,col2\n1,2")

    project_path = hook.get_dbt_project(
        f"s3://{s3_bucket}/project",
        project_dir=str(tmpdir),
    )

    assert project_path.exists()

    dir_contents = [f for f in project_path.iterdir()]
    assert sorted(str(f.name) for f in dir_contents) == [
        "data",
        "dbt_project.yml",
        "models",
    ]

    with open(project_path / "dbt_project.yml") as f:
        result = f.read()
    assert result == project_content

    with open(project_path / "models" / "a_model.sql") as f:
        result = f.read()
    assert result == "SELECT 1"

    with open(project_path / "models" / "another_model.sql") as f:
        result = f.read()
    assert result == "SELECT 2"

    with open(project_path / "data" / "a_seed.csv") as f:
        result = f.read()
    assert result == "col1,col2\n1,2"
