import vminfo_parser.config as config


def test_yaml_load(config_dict: dict, yaml_config: str) -> None:
    conf_obj = config.Config()
    conf_obj.yaml = yaml_config

    conf_obj._load_yaml()

    for key, item in config_dict.items():
        assert getattr(conf_obj, key.replace("-", "_")) == item


def test_yaml_from_args(config_dict: dict, yaml_config: str) -> None:
    conf_obj = config.Config.from_args("--yaml", yaml_config)

    for key, item in config_dict.items():
        assert getattr(conf_obj, key.replace("-", "_")) == item


def test_from_args(config_dict: dict, cli_args: list) -> None:
    conf_obj = config.Config.from_args(*cli_args)

    for key, item in config_dict.items():
        assert getattr(conf_obj, key.replace("-", "_")) == item
