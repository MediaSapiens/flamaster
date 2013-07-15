from __future__ import absolute_import
import re
import json
import hashlib
import os

from flask import current_app
from PIL import Image

from . import settings


EXTENSIONS = settings.EXTENSIONS
DESTINATION = current_app.config.get('THUMBNAIL_DEST', settings.THUMBNAIL_DEST)


size_pattern = re.compile(r'^(\d+)?(?:x(\d+))?$')
crop_pattern = re.compile(r'^(?P<value>\d+)(?P<unit>%|px)$')
kw_pattern = re.compile(r'(?P<key>[\w]+)=(?P<value>[^,]+)')


def to_int(number):
    if isinstance(number, float):
        number = round(number, 0)
    return int(number)


def get_default_options():
    """ Configures default options from built-in settings
    and application settings
    """
    conf = current_app.config
    default_conf = settings.__dict__
    options_list = ('FORMAT', 'QUALITY', 'COLORSPACE', 'UPSCALE',
                    'PROGRESSIVE', 'ORIENTATION')

    def get_option(opt_name):
        attr = "THUMBNAIL_{}".format(opt_name.upper())
        return opt_name, conf.get(attr, default_conf[attr])

    default_options = dict(map(get_option, options_list))
    default_options.update({'CROP': False})

    return default_options


default_options = get_default_options()


class SizeParseError(Exception):

    def __init__(self, exp):
        self.msg = 'Expression does not have the correct syntax: %s' % exp


class Thumbnail(object):

    def __init__(self, img_name, fp, geometry_string, options_string):
        """ Returns fullpath for thumbnail with geometry and
            options given. First it will try to find the thumbnail
            in filesystem, secondly it will create it.
        """
        self.options = self.configure_options(options_string)
        self.image_name = img_name
        thumbnail_name = self.get_name(geometry_string)
        self.thumbnail = os.path.isfile(thumbnail_name) and thumbnail_name
        if not self.thumbnail:
            image = Image.open(fp)
            self.thumbnail = self.create(image, geometry_string, thumbnail_name)

    def get_name(self, geometry_string):
        """ Generates the thumbnail fullpath from a source image name,
            a geometry string and options that passed into request
        """
        salt = '|'.join((self.image_name, geometry_string,
                         json.dumps(sorted(self.options.items()))))
        key = hashlib.md5(salt).hexdigest()
        prefix = DESTINATION
        name = "{}.{}".format(key, EXTENSIONS[self.options['FORMAT']])

        return os.path.join(prefix, key[:2], key[2:4], name)

    def __to_int(self, number):
        if isinstance(number, float):
            number = round(number, 0)
        return int(number)

    def create(self, source_image, geometry_string, thumbnail_name):
        """ Producing some preparatory operations to create a thumbnail
        """
        size = source_image.size
        ratio = float(size[0]) / size[1]
        geometry = self.__parse_geometry(geometry_string, ratio)

        thumbnail = self.transform(source_image, geometry)
        return self.save(thumbnail, thumbnail_name)

    def transform(self, image, geometry):
        """ Sets all options for the thumbnail
        """
        image = self.set_orientation(image, self.options['ORIENTATION'])
        image = self.set_colorspace(image, self.options['COLORSPACE'])
        image = self.set_scale(image, geometry, self.options)
        image = self.set_crop(image, geometry, self.options['CROP'])

        return image

    def save(self, thumbnail, thumbnail_name):
        """ Saves the thumbnail with format and quality options.
            Returns thumbnail fullpath
        """
        params = {
            'FORMAT': self.options['FORMAT'],
            'QUALITY': self.options['QUALITY'],
            'OPTIMIZE': 1
        }
        params['PROGRESSIVE'] = (params['FORMAT'] == 'JPEG')
        path = os.path.dirname(thumbnail_name)

        if not os.path.exists(path):
            os.makedirs(path)

        try:
            thumbnail.save(thumbnail_name, **params)
        except IOError:
            params.pop('OPTIMIZE')
            thumbnail.save(thumbnail_name, **params)

        return thumbnail_name

    def __parse_geometry(self, geometry_string, ratio=None):
        """ Parses a size string syntax and returns a (width, height) tuple
        """
        try:
            width = height = int(geometry_string)
        except ValueError:
            matched = size_pattern.match(geometry_string)

            if matched is None:
                raise SizeParseError(geometry_string)

            width, height = map(int, matched.groups())

        except (AttributeError, TypeError):
            raise SizeParseError(geometry_string)

        if ratio is not None:
            ratio = float(ratio)
            width = height or self.__to_int(height * ratio)
            height = height or self.__to_int(width / ratio)

        return width, height

    def __parse_offset(self, crop, size, new_size):
        """ Returns size value given the crop and
        the difference between size of an image and
        required size

        :param crop:    "12px or 50%"
        :param size:
        :param new_size:
        """
        epsilon = size - new_size
        matched = crop_pattern.match(crop)
        if matched is None:
            raise SizeParseError(crop)

        try:
            value = int(matched.group('value'))
            unit = matched.group('unit')
        except (AttributeError, TypeError):
            raise SizeParseError(crop)

        if unit == '%':
            value = epsilon * value / 100.0

        return int(max(0, min(value, epsilon)))

    def __parse_crop(self, img_size, crop, size=None):
        """ Returns x, y offsets for cropping
        """
        if size is None:
            raise SizeParseError(size)

        alias_percent = ({'left': '0%', 'center': '50%', 'right': '100%'},
                         {'top': '0%', 'center': '50%', 'bottom': '100%'})

        xy_crop = crop.split(' ')
        if len(xy_crop) == 1:
            if crop in alias_percent[0] or crop in alias_percent[1]:
                img_crop = map(lambda d: d.get(crop, '50%'), alias_percent)
            else:
                img_crop = (crop, crop)
        elif len(xy_crop) == 2:
            img_crop = xy_crop
            img_crop = map(lambda d, crop: d.get(crop, crop),
                           alias_percent, img_crop)
        else:
            raise SizeParseError(crop)

        return map(self.__parse_offset, img_crop, img_size, size)

    def __parse_options(self, options_string):
        """ Parses custom options string,
            like 'format=JPEG, colorspace=GRAY'
            into options dictionary.
        """
        options = re.findall(kw_pattern, options_string)
        noresolve = {u'True': True, u'False': False, u'None': None}
        # TODO: how can we get save str?
        options = dict(map(lambda opt: (opt[0], noresolve.get(opt[1], opt[1])),
                           options))
        return options

    def configure_options(self, options_string):
        """ Configures options and default options
        """
        custom_options = self.__parse_options(options_string)
        options = default_options.copy()
        options.update(custom_options)
        if options['COLORSPACE'] not in ['GRAY', 'RGB']:
            options['COLORSPACE'] = default_options['COLORSPACE']
        return options

    def set_orientation(self, image, orientation):
        """ Sets the thumbnail orientation witch depends on
            image metadata
        """
        if orientation:
            try:
                exif = image._getexif()
            except AttributeError:
                exif = None
            if exif:
                orientation = exif.get(0x0112)
                if orientation == 2:
                    image = image.transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 3:
                    image = image.rotate(180)
                elif orientation == 4:
                    image = image.transpose(Image.FLIP_TOP_BOTTOM)
                elif orientation == 5:
                    image = image.rotate(-90).transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 6:
                    image = image.rotate(-90)
                elif orientation == 7:
                    image = image.rotate(90).transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 8:
                    image = image.rotate(90)
        return image

    def set_colorspace(self, image, colorspace):
        """ Translates the thumbnail colorspace, supports only
            'RGB' and 'Grayscale' formats
        """
        if colorspace == 'RGB':
            if image.mode == 'RGBA':
                return image
            if image.mode == 'P' and 'transparency' in image.info:
                return image.convert('RGBA')

            return image.convert('RGB')

        if colorspace == 'GRAY':
            return image.convert('L')

        return image

    def set_scale(self, image, geometry, options):
        """ Resizes thumbnail by an upscale option and
            a crop value
        """
        img_size = map(float, image.size)
        # calculate scaling factor
        factors = (geometry[0] / img_size[0], geometry[1] / img_size[1])
        factor = options['CROP'] and max(factors) or min(factors)
        image_size = map(lambda x: to_int(x * factor), img_size)
        image = image.resize(image_size, resample=Image.ANTIALIAS)
        return image

    def set_crop(self, image, geometry, crop):
        """ Returns a rectangular region from the current image
        """
        if not crop or crop == 'noop':
            return image
        img_size = image.size
        x_offset, y_offset = self.__parse_crop(img_size, crop, geometry)

        return image.crop((x_offset, y_offset, geometry[0] + x_offset,
                           geometry[0] + y_offset))
