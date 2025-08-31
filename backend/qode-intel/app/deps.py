from app.services.scraper.playwright_client import PlaywrightClient


class ScrapeBackend:
    def __init__(self):
        self.pw = PlaywrightClient()

    def get(self):
        return self


backend_singleton = ScrapeBackend()


def get_backend():
    return backend_singleton
