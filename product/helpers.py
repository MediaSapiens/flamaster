# -*- encoding: utf-8 -*-
from .models import Category


def resolve_parent(data):
    parent_id = data.pop('parent_id', None)

    if parent_id is not None:
        data['parent'] = Category.query.get_or_404(parent_id)

    return data
