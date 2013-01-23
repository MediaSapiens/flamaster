import re
import json
import hashlib
import os

from flask import current_app
from PIL import Image

from . import settings


EXTENSIONS = current_app.config.get('EXTENSIONS', settings.EXTENSIONS)
DESTINATION = current_app.config.get('THUMBNAIL_DEST', settings.THUMBNAIL_DEST)


size_pat = re.compile(r'^(\d+)?(?:x(\d+))?$')
crop_pat = re.compile(r'^(?P<value>\d+)(?P<unit>%|px)$')
kw_pat = re.compile(r'(?P<key>[\w]+)=(?P<value>[^,]+)')


class SizeParseError(Exception):

    def __init__(self, exp):
        self.msg = 'Expression does not have the correct syntax: %s' % exp


def get_default_options():
    """Configures default options from built-in settings
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


def toint(number):
    if isinstance(number, float):
        number = round(number, 0)
    return int(number)


def get_geometry(geometry_string, ratio=None):
    """
    Parses a size string syntax and returns a (width, height) tuple
    """
    try:
        x = y = int(geometry_string)
    except ValueError:
        m = size_pat.match(geometry_string)
        x, y = map(int, m.groups())
    except (AttributeError, TypeError):
        raise SizeParseError(geometry_string)

    if ratio is not None:
        ratio = float(ratio)
        x = x or toint(y * ratio)
        y = y or toint(x / ratio)

    return x, y


def get_offset(crop, size, new_size):
    """Returns size value given the crop and
    the difference between size of an image and
    required size
    """
    epsilon = size - new_size
    m = crop_pat.match(crop)
    try:
        value = int(m.group('value'))
        unit = m.group('unit')
    except (AttributeError, TypeError):
        raise SizeParseError(crop)

    if unit == '%':
        value = epsilon * value / 100.0

    return int(max(0, min(value, epsilon)))


def get_crop(img_size, crop, size=None):
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

    return map(get_offset, img_crop, img_size, size)


def get_thumbnail_name(image_name, geometry_string, options):
    """Generates the thumbnail fullpath from a source image name,
       a geometry string and options that passed into request
    """
    salt = '|'.join((image_name, geometry_string,
                        json.dumps(sorted(options.items()))))
    key = hashlib.md5(salt).hexdigest()
    prefix = DESTINATION
    name = "{}.{}".format(key, EXTENSIONS[options['FORMAT']])

    return os.path.join(prefix, key[:2], key[2:4], name)


def set_orientation(image, orientation):
    """Sets the thumbnail orientation witch depends on
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


def set_colorspace(image, colorspace):
    """Translates the thumbnail colorspace, supports only
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


def set_scale(image, geometry, options):
    """Resizes thumbnail by an upscale option and
       a crop value
    """
    img_size = map(float, image.size)
    # calculate scaling factor
    factors = (geometry[0] / img_size[0], geometry[1] / img_size[1])
    factor = options['CROP'] and max(factors) or min(factors)
    image_size = map(lambda x: toint(x * factor), img_size)
    image = image.resize(image_size, resample=Image.ANTIALIAS)
    return image


def set_crop(image, geometry, crop):
    """Returns a rectangular region from the current image
    """
    if not crop or crop == 'noop':
        return image
    img_size = image.size
    x_offset, y_offset = get_crop(img_size, crop, geometry)

    return image.crop((x_offset, y_offset,
                           geometry[0] + x_offset, geometry[0] + y_offset))


def set_options(image, geometry, options):
    """
    Sets all options for the thumbnail
    """
    image = set_orientation(image, options['ORIENTATION'])
    image = set_colorspace(image, options['COLORSPACE'])
    image = set_scale(image, geometry, options)
    image = set_crop(image, geometry, options['CROP'])

    return image


def save_thumbnail(thumbnail, thumbnail_name, options):
    """Saves the thumbnail with format and quality options.
       Returns thumbnail fullpath
    """
    params = {
        'FORMAT': options['FORMAT'],
        'QUALITY': options['QUALITY'],
        'OPTIMIZE': 1
    }
    params['PROGRESSIVE'] = (params['FORMAT'] == 'JPEG')
    path = os.path.dirname(thumbnail_name)
    os.path.exists(path) or os.makedirs(path)
    try:
        thumbnail.save(thumbnail_name, **params)
    except IOError:
        params.pop('OPTIMIZE')
        thumbnail.save(thumbnail_name, **params)

    return thumbnail_name


def create_thumbnail(source_image, geometry_string, thumbnail_name, options):
    """Producing some preparatory operations to create a thumbnail
    """
    size = source_image.size
    ratio = float(size[0]) / size[1]
    geometry = get_geometry(geometry_string, ratio)
    thumbnail = set_options(source_image, geometry, options)
    return save_thumbnail(thumbnail, thumbnail_name, options)


def parse_options(options_string):
    """Parses custom options string,
       like 'format=JPEG, colorspace=GRAY'
       into options dictionary.
    """
    options = re.findall(kw_pat, options_string)
    noresolve = {u'True': True, u'False': False, u'None': None}
    # TODO: how can we get save str?
    options = dict(map(lambda opt: (opt[0], noresolve.get(opt[1], opt[1])),
                       options))
    return options


def configure_options(options_string):
    """Configures options and default options
    """
    custom_options = parse_options(options_string)
    options = default_options.copy()
    options.update(custom_options)
    if options['COLORSPACE'] not in ['GRAY', 'RGB']:
        options['COLORSPACE'] = default_options['COLORSPACE']
    return options


def get_thumbnail(img_name, fp, geometry_string, options_string):
    """
    Returns fullpath for thumbnail with geometry and
    options given. First it will try to find the thumbnail
    in filesystem, secondly it will create it.
    """
    options = configure_options(options_string)
    thumbnail_name = get_thumbnail_name(img_name, geometry_string, options)
    print thumbnail_name
    thumbnail = os.path.isfile(thumbnail_name) and thumbnail_name
    if not thumbnail:
        image = Image.open(fp)
        thumbnail = create_thumbnail(image, geometry_string,
                                     thumbnail_name, options)
    return thumbnail
