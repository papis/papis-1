import re
from typing import Optional

import papis.downloaders.base


class Downloader(papis.downloaders.Downloader):

    def __init__(self, url: str):
        papis.downloaders.Downloader.__init__(
            self, url, name="acm")
        self.expected_document_extension = "pdf"
        self.cookies = {"gdpr": "true"}

    @classmethod
    def match(cls, url: str) -> Optional[papis.downloaders.Downloader]:
        if re.match(r".*acm.org.*", url):
            return Downloader(url)
        else:
            return None

    def get_doi(self) -> Optional[str]:
        url = self.uri
        self.logger.debug("Parsing DOI from '%s'", url)
        mdoi = re.match(r".*/doi/(.*/[^?&%^$]*).*", url)
        if mdoi:
            doi = mdoi.group(1).replace("abs/", "").replace("full/", "")
            return doi

        return None

    def get_document_url(self) -> Optional[str]:
        durl = ("https://dl.acm.org/doi/pdf/{doi}"
                .format(doi=self.get_doi()))
        self.logger.debug("doc url = '%s'", durl)
        return durl
