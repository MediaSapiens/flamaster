# encoding: utf-8
from __future__ import absolute_import
from flask import render_template, request, current_app
from flask.ext.security import login_required

from . import bp
from .models import FlatPage


# TODO: need to decide, how we handle 404 error?
@bp.after_app_request
def view_flatpage(response):
    if response.status_code == 404:
        path = request.path.strip('/')
        page = FlatPage.query.filter_by(slug=path).first()
        if page is not None:
            template = page.template_name or 'flatpage.html'
            make_content = render_template
            if page.registration_required is True:
                make_content = login_required(render_template)
            return current_app.make_response(make_content(template, page=page))

    return response

# def get_flatpage(slug):
#     slug = slug and slug.strip('/')
#     page = FlatPage.query.filter_by(slug=slug).first()
#     if page is not None:
#         template = page.template_name or 'flatpage.html'
#         make_content = render_template
#         if page.registration_required is True:
#             make_content = login_required(render_template)
#         return current_app.make_response(make_content(template, page=page))
