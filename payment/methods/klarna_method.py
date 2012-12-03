from klarna import Klarna, Config

from .base import BasePaymentMethod

# TODO: add to Config args. Use data from request.
country = 'SE'
currency = 'SEK'

class KlarnaPaymentMethod(BasePaymentMethod):
    method_name = 'klarna'
    def __init__(self, *args, **kwargs):
        super(KlarnaPaymentMethod, self).__init__(*args, **kwargs)

        self.klarna = Klarna(Config(**self.settings))
        self.klarna.init()

    def init_payment(self):
        art_list = []
        good_list = self.__get_articles(art_list)
        return self.klarna.add_transaction(gender=1, pno='860728-1234',
                    goodList=good_list)

    def __get_articles(self, art_list): #qty, artno, price, vat):
        for art in art_list:
            yield self.klarna.add_article(qty=art['qty'], artno=art['artno'],
                    price=art['price'], vat=art['vat'])
