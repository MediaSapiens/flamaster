# encoding: utf-8
import trafaret as t

from flamaster.core import http
from flamaster.core.decorators import api_resource
from flamaster.core.resources import ModelResource
from flamaster.core.utils import jsonify_status_code

from flask import abort, g, request
from flask.ext.security import login_required, current_user

from werkzeug import FileStorage

from sqlalchemy import or_

from . import bp
from .models import Image, Album


def get_access_type(data_dict):
    album = Album.query.get(data_dict['album_id']) or abort(http.BAD_REQUEST)
    is_public = data_dict.get('is_public', True) and album.is_public
    data_dict['is_public'] = is_public
    return data_dict


@api_resource(bp, 'images', {'id': int})
class ImageResource(ModelResource):
    model = Image

    validation = t.Dict({
        'album_id': t.Int,
        'image': t.Type(FileStorage),
    }).make_optional('album_id').ignore_extra('*')

    method_decorators = {'post': [login_required],
                         'put': [login_required],
                         'delete': [login_required]}

    def post(self):
        status = http.CREATED
        data = request.form.to_dict()
        try:
            data['image'] = request.files.get('image')
            data = self.validation.check(data)
            print data['image']
            data['author_id'] = current_user.id
            response = self.model.create(**data).as_dict()
        except t.DataError as e:
            status, response = http.BAD_REQUEST, e.as_dict()

        return jsonify_status_code(response, status)

    def get(self, id=None):
        # validation = self.validation.append(get_access_type)

        kwargs = request.args.to_dict()

        if id is None:
            kwargs['page'] = int(request.args.get('page', 1))
            response = self.gen_list_response(**kwargs)
        else:
            response = self.get_object(id).as_dict()

        return jsonify_status_code(response)

    def _normalize(self, kwargs):
        boolean = {u'true': True, u'False': False}
        for k, v in kwargs.iteritems():
            v in boolean and kwargs.__setitem__(k, boolean[v])
            v.isdigit() and kwargs.__setitem__(k, int(v))

        return kwargs

    def get_objects(self, **kwargs):
        """ Method for extraction object list query
        """
        query = super(ImageResource, self).get_objects(**kwargs)
        if current_user.is_anonymous():
            return query.filter_by(is_public=True)
        elif current_user.is_superuser:
            return query
        else:
            return query.filter(or_(self.model.author_id == current_user.id,
                                       self.model.is_public is True))


# TODO: Establish why GET params does not pass to request.args
@api_resource(bp, 'albums', {'id': int})
class AlbumResource(ImageResource):
    model = Album

    validation = t.Dict({
        'name': t.String,
        'description': t.String,
        'coverage': t.Dict({'id': t.Int}).ignore_extra('*')
    }).ignore_extra('*')

    def post(self, owner=None):
        #TODO: how to set an owner?
        author = g.user.is_anonymous() and abort(http.UNAUTHORIZED) or g.user
        request.json.update({'author': author})
#        if owner is not None:
#            request.json.update({'owner': owner})
        return super(ImageResource, self).post()
