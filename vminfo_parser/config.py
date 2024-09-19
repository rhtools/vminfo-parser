import argparse
import typing as t

import yaml


def _get_parser() -> argparse.ArgumentParser:
    """Create ArguementParser object and add arguements to it.
    This is separated into its own function to increase readability.

    Returns:
        argparse.ArgumentParser: ArgumentParser object configured for all cli options.
    """
    parser = argparse.ArgumentParser(description="Process VM CSV file")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", type=str, help="The file to parse")
    group.add_argument("--yaml", type=str, help="Path to YAML configuration file")

    parser.add_argument(
        "--sort-by-env",
        type=str,
        nargs="?",
        default=None,
        help='Sort disk by environment. Use "all" to get combine count, '
        '"both" to show both non-prod and prod, or specify one.',
    )
    parser.add_argument(
        "--sort-by-site",
        action="store_true",
        default=False,
        help="Generate per-site stats.",
    )
    parser.add_argument(
        "--prod-env-labels",
        type=str,
        nargs="?",
        default=None,
        help="The values in your data that represent prod environments. "
        "This is used to generate prod and non-prod stats. "
        "Passed as CSV i.e. --prod-env-labels 'baker,dte'",
    )
    parser.add_argument(
        "--generate-graphs",
        action="store_true",
        default=False,
        help="Choose whether or not to output visual graphs. "
        "If this option is not set, a text table will be outputted to the terminal",
    )
    parser.add_argument(
        "--get-disk-space-ranges",
        action="store_true",
        default=False,
        help="This flag will get disk space ranges regardless of OS. "
        "Can be combine with --prod-env-labels and --sort-by-env to target a specific environment",
    )
    parser.add_argument(
        "--show-disk-space-by-os",
        action="store_true",
        default=False,
        help="Show disk space by OS",
    )
    parser.add_argument(
        "--breakdown-by-terabyte",
        action="store_true",
        default=False,
        help="Breaks disk space down into 0-2TB, 2-9TB and 9TB+ instead of the default categories",
    )
    parser.add_argument(
        "--over-under-tb",
        action="store_true",
        default=False,
        help="A simple break down of machines under 1TB and those over 1TB",
    )
    parser.add_argument(
        "--output-os-by-version",
        action="store_true",
        default=False,
        help="Output OS by version",
    )
    parser.add_argument(
        "--get-os-counts",
        action="store_true",
        default=False,
        help="Generate a report that counts the inventory broken down by OS",
    )
    parser.add_argument(
        "--os-name",
        type=str,
        default=None,
        help="The name of the Operating System to produce a report about",
    )
    parser.add_argument(
        "--minimum-count",
        type=int,
        default=0,
        help="Anything below this number will be excluded from the results",
    )
    parser.add_argument(
        "--get-supported-os",
        action="store_true",
        default=False,
        help="Display a graph of the supported operating systems for OpenShift Virt",
    )
    parser.add_argument(
        "--get-unsupported-os",
        action="store_true",
        default=False,
        help="Display a graph of the unsupported operating systems for OpenShift Virt",
    )

    return parser


def _parse_fail(msg: str) -> None:
    print(msg)
    _get_parser().print_help()
    exit(1)


class Config:
    def __init__(self: t.Self, **kwargs: t.Any) -> None:
        for name in kwargs:
            setattr(self, name, kwargs[name])

    def __contains__(self: t.Self, key: str) -> bool:
        return key in self.__dict__

    @classmethod
    def from_args(cls: t.Self, *args: str) -> t.Self:
        """Create Config object from passed arguements or sys.argv

        Args:
            *args (str): strings to be interpreted as command line arguements.

        Returns:
            Config: Config object with all parsed arguements as attributes
        """
        parser = _get_parser()
        config = cls()
        if not args:
            args = None
        parser.parse_args(args=args, namespace=config)

        # Check if --yaml is used and exit if other arguments are provided
        if config.yaml:
            if any(getattr(config, arg) for arg in vars(config) if arg != "yaml"):
                _parse_fail("When using --yaml, no other arguments should be provided.")
            config._load_yaml()
        elif not config.file:
            # this is likely never reachable because argparse forces it.
            _parse_fail("--file is required when --yaml is not used.")

        config._validate()
        return config

    def _load_yaml(self: t.Self) -> None:
        """Read yaml file and add arguements as attributes to Config object.
        Does not override non-default attributes set elsewhere.
        """
        try:
            with open(self.yaml, "r") as yaml_file:
                config_dict = yaml.safe_load(yaml_file)
                # Convert dash-separated keys to underscore-separated keys
                for key, value in config_dict.items():
                    new_key = key.replace("-", "_")
                    if getattr(self, new_key, None):
                        print(f"Ignoring {new_key} from yaml, already set.")
                    else:
                        setattr(self, new_key, value)
            delattr(self, "yaml")

        except FileNotFoundError:
            print(f"YAML file not found: {self.yaml}")
            exit(1)
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")
            exit(1)

    def load_from_env(self: t.Self) -> None:
        # Implement loading configuration from environment variables
        pass

    def _validate(self: t.Self) -> None:
        """Ensure that necessary options are available for parser to function."""

        # TODO: implement further validation or force yaml through argparse validation.
        # perhaps using subparsers for yaml and everything else
        if not hasattr(self, "file"):
            print("File not specified in yaml or command line")
            exit(1)
