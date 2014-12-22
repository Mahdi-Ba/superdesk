import superdesk
from superdesk.io.ingest_provider_model import DAYS_TO_KEEP
from superdesk.errors import ProviderError


class AddProvider(superdesk.Command):
    """Add ingest provider."""

    option_list = {
        superdesk.Option('--provider', '-p', dest='provider'),
    }

    def run(self, provider=None):
        try:
            if provider:
                data = superdesk.json.loads(provider)
                data.setdefault('name', data['type'])
                data.setdefault('source', data['type'])
                data.setdefault('days_to_keep', DAYS_TO_KEEP)
                db = superdesk.get_db()
                db['ingest_providers'].save(data)
                return data
        except Exception as ex:
            raise ProviderError.providerAddError(ex)

superdesk.command('ingest:provider', AddProvider())
