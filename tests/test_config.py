import logging
import pathlib
import sys

import pytest

from vminfo_parser.config import Config


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


def test_validate(caplog: pytest.LogCaptureFixture) -> None:
    config_obj = Config()

    with pytest.raises(SystemExit):
        config_obj._validate()

    assert caplog.record_tuples == [
        ("vminfo_parser.config", logging.CRITICAL, "File not specified in yaml or command line")
    ]


def test_cli_yaml_and_args(capsys: pytest.CaptureFixture, caplog: pytest.LogCaptureFixture) -> None:
    with pytest.raises(SystemExit):
        Config.from_args("--yaml", "filename", "--os-name", "osname")
    output = capsys.readouterr()
    assert caplog.record_tuples == [
        ("vminfo_parser.config", logging.ERROR, "When using --yaml, no other arguments should be provided.")
    ]
    assert "usage:" in output.err
    assert "[-h] (--file FILE | --yaml YAML)" in output.err


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
