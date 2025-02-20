import os
from typing import Optional, List, Dict, Any, Sequence

import yaml                                 # lgtm [py/import-and-import-from]
import click

import papis.utils
import papis.config
import papis.importer
import papis.document
import papis.logging

# NOTE: try to use the CLoader when possible, as it's a lot faster than the
# python version, at least at the time of writing
try:
    from yaml import CSafeLoader as Loader
except ImportError:
    from yaml import SafeLoader as Loader  # type: ignore[assignment]

logger = papis.logging.get_logger(__name__)

YAML_LOADER = Loader


def data_to_yaml(yaml_path: str, data: Dict[str, Any]) -> None:
    """
    Save data to yaml at path outpath

    :param yaml_path: Path to a yaml file
    :param data: Data in a dictionary
    """
    with open(yaml_path, "w+") as fd:
        yaml.dump(
            data,
            fd,
            allow_unicode=papis.config.getboolean("info-allow-unicode"),
            default_flow_style=False)


def yaml_to_list(yaml_path: str,
                 raise_exception: bool = False) -> Sequence[Dict[str, Any]]:
    """
    Analogous to yaml_to_data but using load_all to read everything.
    """
    try:
        with open(yaml_path) as fdd:
            return list(yaml.load_all(fdd, Loader=Loader))
    except Exception as e:
        if raise_exception:
            raise ValueError(e) from e
        logger.error("YAML syntax error. %s")
        return []


def list_to_path(data: Sequence[Dict[str, Any]], filepath: str) -> None:
    with open(filepath, "w+") as fdd:
        yaml.dump_all(data, fdd, allow_unicode=True)


def exporter(documents: List[papis.document.Document]) -> str:
    """
    Returns a yaml string containing all documents in the input list.
    """
    string = yaml.dump_all(
        [papis.document.to_dict(document) for document in documents],
        allow_unicode=True)
    return str(string)


def yaml_to_data(
        yaml_path: str,
        raise_exception: bool = False) -> Dict[str, Any]:
    """
    Convert a yaml file into a dictionary using the yaml module.

    :param yaml_path: Path to a yaml file
    :returns: Dictionary containing the info of the yaml file
    :raises ValueError: If a yaml parsing error happens
    """
    with open(yaml_path) as fd:
        try:
            data = yaml.load(fd, Loader=Loader)
        except Exception as e:
            if raise_exception:
                raise ValueError(e) from e
            logger.error("YAML syntax error. %s", e)
            return {}
        else:
            assert isinstance(data, dict)
            return data


@click.command("yaml")
@click.pass_context
@click.argument("yamlfile", type=click.Path(exists=True))
@click.help_option("--help", "-h")
def explorer(ctx: click.Context, yamlfile: str) -> None:
    """
    Import documents from a yaml file

    Examples of its usage are

    papis explore yaml lib.yaml pick

    """
    logger.info("Reading in yaml file '%s'", yamlfile)

    with open(yamlfile) as fd:
        docs = [papis.document.from_data(d)
                for d in yaml.load_all(fd, Loader=Loader)]
    ctx.obj["documents"] += docs

    logger.info("%d documents found", len(docs))


class Importer(papis.importer.Importer):

    """Importer that parses a yaml file"""

    def __init__(self, uri: str) -> None:
        super().__init__(name="yaml", uri=uri)

    @classmethod
    def match(cls, uri: str) -> Optional[papis.importer.Importer]:
        importer = Importer(uri=uri)
        if os.path.exists(uri) and not os.path.isdir(uri):
            importer.fetch()
            return importer if importer.ctx.data else None
        return None

    def fetch_data(self: papis.importer.Importer) -> Any:
        self.ctx.data = yaml_to_data(self.uri, raise_exception=True)
        if self.ctx:
            self.logger.debug("Successfully read file: '%s'.", self.uri)
