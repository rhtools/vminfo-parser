import logging
import pathlib
import sys

import pytest
import yaml

from vminfo_parser.config import Config

from .. import const as test_const


def test_yaml_load(config_dict: dict, yaml_config: str) -> None:
    config_obj = Config(yaml=yaml_config)

    config_obj._load_yaml()

    assert_config_correct(config_dict, config_obj)


def test_yaml_load_file_not_found(tmp_path: pathlib.Path, caplog: pytest.LogCaptureFixture) -> None:
    yamlfile = str(tmp_path / "config.yaml")
    config_obj = Config(yaml=yamlfile)

    with pytest.raises(SystemExit):
        config_obj._load_yaml()

    assert caplog.record_tuples == [("vminfo_parser.config", logging.CRITICAL, "YAML file not found: %s" % yamlfile)]


def test_yaml_load_invalid_file(tmp_path: pathlib.Path, caplog: pytest.LogCaptureFixture) -> None:
    yamlfile = str(tmp_path / "config.yaml")
    with open(yamlfile, "w") as file:
        file.write("value: !invalid\n")
    config_obj = Config(yaml=yamlfile)

    with pytest.raises(SystemExit):
        config_obj._load_yaml()

    assert caplog.record_tuples == [("vminfo_parser.config", logging.CRITICAL, "Error parsing YAML file")]


def test_yaml_load_duplicate(tmp_path: pathlib.Path, caplog: pytest.LogCaptureFixture) -> None:
    yamlfile = str(tmp_path / "config.yaml")
    with open(yamlfile, "w") as file:
        file.write("test-value: test")
    config_obj = Config(yaml=yamlfile, test_value="original")
    config_obj._load_yaml()

    assert config_obj.test_value == "original"
    assert caplog.record_tuples == [
        ("vminfo_parser.config", logging.WARNING, "Ignoring test_value from yaml, already set.")
    ]


def test_cli_yaml_and_args(capsys: pytest.CaptureFixture, caplog: pytest.LogCaptureFixture) -> None:
    with pytest.raises(SystemExit):
        Config.from_args("--yaml", "filename", "--os-name", "osname")
    output = capsys.readouterr()
    assert caplog.record_tuples == [
        ("vminfo_parser.config", logging.ERROR, "When using --yaml, no other arguments should be provided.")
    ]
    assert "usage:" in output.err
    assert "[-h] [--file FILE | --yaml YAML | --directory DIRECTORY]" in output.err


def test_yaml_from_args(config_dict: dict, yaml_config: str) -> None:
    config_obj = Config.from_args("--yaml", yaml_config)

    assert_config_correct(config_dict, config_obj)


def test_from_args(config_dict: dict, cli_args: list) -> None:
    config_obj = Config.from_args(*cli_args)

    assert_config_correct(config_dict, config_obj)


def test_from_sys_argv(config_dict: dict, cli_args: list, monkeypatch: pytest.MonkeyPatch) -> None:
    with monkeypatch.context() as m:
        m.setattr(sys, "argv", ["run_pytest_script.py"] + cli_args, raising=False)
        config_obj = Config.from_args()
    assert_config_correct(config_dict, config_obj)


def assert_config_correct(config_dict: dict, config_obj: Config) -> None:
    for key, item in config_dict.items():
        assert getattr(config_obj, key.replace("-", "_")) == item


def test_generate_yaml_from_parser(tmp_path: pathlib.Path) -> None:
    config_obj = Config.from_args("--generate-yaml", "--file", "testfile.yaml")
    tmp_file = tmp_path / "config.yaml"
    config_obj.generate_yaml_from_parser(tmp_file)

    with open(tmp_file, "r") as generated_file:
        generated_yaml = yaml.safe_load(generated_file)
    assert generated_yaml == test_const.EXPECTED_ARGPARSE_TO_YAML


@pytest.mark.parametrize("labels", ["env1,env2", "env1", None], ids=["multiple", "single", "none"])
def test_environments(labels: str | None) -> None:
    expected = labels.split(",") if labels else []
    result = Config(prod_env_labels=labels).environments

    assert result == expected


@pytest.mark.parametrize("sort_by_env", ["all", "both", "env1", None])
def test_environment_filter(sort_by_env: str | None) -> None:
    expected = sort_by_env if sort_by_env else "all"
    result = Config(sort_by_env=sort_by_env).environment_filter

    assert result == expected


@pytest.mark.parametrize("counts", [0, 100, 500])
def test_count_filter(counts: int) -> None:
    expected = counts if counts > 0 else None
    result = Config(minimum_count=counts).count_filter

    assert result == expected


def test_validate(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.CRITICAL):
        Config(file="testfile", sort_by_env="all")._validate()
    assert caplog.get_records("call") == []


def test_validate_no_file(caplog: pytest.LogCaptureFixture) -> None:
    with pytest.raises(SystemExit):
        Config()._validate()

    assert caplog.record_tuples == [
        ("vminfo_parser.config", logging.CRITICAL, "File not specified in yaml or command line")
    ]


def test_validate_missing_env(caplog: pytest.LogCaptureFixture) -> None:
    with pytest.raises(SystemExit):
        Config(file="testfile", sort_by_env="both", prod_env_labels=None)._validate()

    assert caplog.record_tuples == [
        (
            "vminfo_parser.config",
            logging.CRITICAL,
            (
                "You specified you wanted to sort by environment but "
                "did not provide a definition of what categorizes a Prod environment... exiting"
            ),
        )
    ]
