from flask import Flask, render_template


app = Flask(__name__)
app.config.from_object('conf.settings')

# blueprints sections
blueprints = ['account', 'category', 'delivery', 'image', 'order', 'payment',
    'pricing', 'product', 'reporting', 'statistic', 'stock', 'tax'
]

for name in blueprints:
    module_name = 'core.%s' % name
    bp_module = __import__(module_name, {}, {}, [''])
    bp = getattr(bp_module, name)
    app.register_blueprint(bp)


# handling error pages
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(403)
def access_denied(e):
    return render_template('403.html'), 403
