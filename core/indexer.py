import logging
from flask import current_app
from mongoengine import signals
from operator import methodcaller
from requests.exceptions import ConnectionError

from flamaster.core.utils import CustomEncoder
from flamaster.extensions import es


__all__ = ['BaseIndex', 'MongoDocumentIndex', 'Index', 'index']


logger = logging.getLogger('indexer')

@signals.post_save.connect
def put_on_index(cls, document, created):
    if created:
        index.process(cls, document, action=Index.CREATE)
    else:
        index.process(cls, document, action=Index.UPDATE)


@signals.post_bulk_insert.connect
def put_all_on_index(cls, documents, loaded):
    index.process(cls, documents, in_bulk=True)


class BaseIndex(object):

    index_type = None

    def __init__(self):
        if self.index_type is None:
            # pass
            raise RuntimeError('Index type is not defined')

    def get_data(self, cls):
        raise NotImplementedError()

    def create(self, cls, document=None):
        raise NotImplementedError()

    def update(self, cls, document=None):
        raise NotImplementedError()


class MongoDocumentIndex(BaseIndex):

    def get_data(self, cls):
        return cls.objects

    def create(self, cls, document=None, in_bulk=False):
        self.index = current_app.config['INDEX_NAME']
        if in_bulk:
            documents = document or self.get_data(cls)
            iobjects = map(lambda d: d.as_dict(), documents)
            es.bulk_index(self.index, self.index_type, iobjects,
                          refresh=True)
        else:
            iobject = document.as_dict()
            es.index(self.index, self.index_type, iobject, id=iobject['id'],
                     refresh=True)

    def update(self, cls, document=None, in_bulk=False):
        return self.create(cls, document, in_bulk)

    def delete(self, cls, document):
        es.delete(self.index, self.index_type, str(document.id), refresh=True)

    def clean(self):
        es.delete_all(self.index, self.index_type)

    def search(self, query):
        # {'query': {'match': {'name': 'some place'}}}
        return es.search(query, index=self.index, doc_type=self.index_type)

class Index(object):

    CREATE = 'create'
    UPDATE = 'update'

    def __init__(self):
        self.registry = {}

    def add(self, cls, index_cls):
        if cls in self.registry:
            raise Exception('Model already registered')
        else:
            self.registry[cls] = index_cls()

    def remove(self, cls):
        if cls in self.registry:
            del self.registry[cls]
        else:
            raise Exception('Model not registered')

    def _patch_encoder(self):
        current_app.extensions['elasticsearch'].json_encoder = CustomEncoder

    def process(self, cls, doc_or_docs, action, **kwargs):
        """ Processing data changes on registered objects

        :param cls: Indexed object class
        :param doc_or_docs: Indexed object instance
        :param action: Action to perform on index
        :param kwargs: additional keyword args would be passed to `BaseIndex`
                subclass
        """
        self._patch_encoder()
        index_cls = self.registry.get(cls)
        if index_cls is not None:
            applicator = methodcaller(action, cls, document=doc_or_docs,
                                      **kwargs)
            try:
                applicator(index_cls)
            except ConnectionError as err:
                logger.critical('ElasticSearch node unreachable')

        else:
            pass
            # current_app.logger.debug("Model %s not registered", cls)

    def reindex(self):
        """
        Reindex all registered objects
        """
        self._patch_encoder()
        for model_cls, index_cls in self.registry.iteritems():
            index_cls.create(model_cls, in_bulk=True)


index = Index()
