=========
fevent
=========

-------------------------------
E-commerce eventing system
-------------------------------

Setup requirements:
___________________

- Python == v2.7.x
- `Flask <http://flask.pocoo.org>`__ >= 0.8
- `Flask-Script <http://packages.python.org/Flask-Script/>`__ >= 0.3.1 (for shell commands support)
- `Flask-SQLAlchemy <http://packages.python.org/Flask-SQLAlchemy/>`__ >= 0.15
- `Flask-Mail <http://packages.python.org/flask-mail/>`__ >= 0.6.1
- `Flask-MongoSet <http://pypi.python.org/pypi/Flask-MongoSet/>`__ >= 0.1.8
- `Flask-Social`
- `Flask-Security`

Testing:
________

- `nosetests <https://nose.readthedocs.org/en/latest/>`__

================
Running project:
================

You should implement your own Cart and Order models based on `flamaster.product.mixins` and register it on your local settings
for each shop you'd connect:

```python
SHOPS = [
    {
        'cart': 'findevent.vending.models.Cart',
        'order': 'findevent.vending.models.Order'
    }
]
```
