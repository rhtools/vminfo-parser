import pathlib

import pytest

import vminfo_parser.config as config


def test_yaml_load(config_dict: dict, yaml_config: str) -> None:
    conf_obj = config.Config(yaml=yaml_config)

    conf_obj._load_yaml()

    for key, item in config_dict.items():
        assert getattr(conf_obj, key.replace("-", "_")) == item


def test_yaml_load_file_not_found(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture) -> None:
    yamlfile = str(tmp_path / "config.yaml")
    conf_obj = config.Config(yaml=yamlfile)

    with pytest.raises(SystemExit):
        conf_obj._load_yaml()
    output = capsys.readouterr()
    assert output.out == f"YAML file not found: {yamlfile}\n"


def test_yaml_load_invalid_file(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture) -> None:
    yamlfile = str(tmp_path / "config.yaml")
    with open(yamlfile, "w") as file:
        file.write("value: !invalid\n")
    conf_obj = config.Config(yaml=yamlfile)

    with pytest.raises(SystemExit):
        conf_obj._load_yaml()
    output = capsys.readouterr()
    assert "Error parsing YAML file:" in output.out


def test_yaml_load_duplicate(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture) -> None:
    yamlfile = str(tmp_path / "config.yaml")
    with open(yamlfile, "w") as file:
        file.write("test-value: test")
    conf_obj = config.Config(yaml=yamlfile, test_value="original")
    conf_obj._load_yaml()

    output = capsys.readouterr()
    assert conf_obj.test_value == "original"
    assert output.out == "Ignoring test_value from yaml, already set.\n"


def test_validate(capsys: pytest.CaptureFixture) -> None:
    conf_obj = config.Config()

    with pytest.raises(SystemExit):
        conf_obj._validate()
    output = capsys.readouterr()
    assert output.out == "File not specified in yaml or command line\n"


def test_cli_yaml_and_args(capsys: pytest.CaptureFixture) -> None:
    with pytest.raises(SystemExit):
        config.Config.from_args("--yaml", "filename", "--os-name", "osname")
    output = capsys.readouterr()
    assert "When using --yaml, no other arguments should be provided.\n" in output.out
    assert "usage:" in output.out


def test_yaml_from_args(config_dict: dict, yaml_config: str) -> None:
    conf_obj = config.Config.from_args("--yaml", yaml_config)

    for key, item in config_dict.items():
        assert getattr(conf_obj, key.replace("-", "_")) == item


def test_from_args(config_dict: dict, cli_args: list) -> None:
    conf_obj = config.Config.from_args(*cli_args)

    for key, item in config_dict.items():
        assert getattr(conf_obj, key.replace("-", "_")) == item
