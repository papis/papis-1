from ..document import Document
import papis
import os
import papis.utils
from . import Command


class Check(Command):
    def init(self):
        """TODO: Docstring for init.

        :subparser: TODO
        :returns: TODO

        """
        self.subparser = self.parser.add_parser(
            "check",
            help="Check document document from a given library"
        )
        self.subparser.add_argument(
            "document",
            help="Document search",
            nargs="?",
            default=".",
            action="store"
        )
        self.subparser.add_argument(
            "--keys", "-k",
            help="Key to check",
            nargs="*",
            default=[],
            action="store"
        )

    def main(self, config, args):
        """
        Main action if the command is triggered

        :config: User configuration
        :args: CLI user arguments
        :returns: TODO

        """
        documentsDir = os.path.expanduser(config[args.lib]["dir"])
        self.logger.debug("Using directory %s" % documentsDir)
        documentSearch = args.document
        documents = papis.utils.getFilteredDocuments(
            documentsDir,
            documentSearch
        )
        allOk = True
        for document in documents:
            allOk &= document.checkFile()
            for key in args.keys:
                if key not in document.keys():
                    allOk &= False
                    print(
                        "%s not found in %s" % (key, document.getMainFolder())
                    )
        if not allOk:
            print("Errors were detected, please fix the info files")
        else:
            print("No errors detected")
