class AbstractDatastore(object):

    def find_one(self, **kwargs):
        raise NotImplementedError

    def find(self, **kwargs):
        raise NotImplementedError
