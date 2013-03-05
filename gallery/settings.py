# encoding: utf-8

THUMBNAIL_DEST = 'cache/'

THUMBNAIL_FORMAT = 'JPEG'

# Colorspace, backends are required to implement: RGB, GRAY
THUMBNAIL_COLORSPACE = 'RGB'

# Should we upscale images by default
THUMBNAIL_UPSCALE = True

# Quality, 0-100
THUMBNAIL_QUALITY = 95

# Save as progressive when saving as jpeg
THUMBNAIL_PROGRESSIVE = True

# Orientate the thumbnail with respect to source EXIF orientation tag
THUMBNAIL_ORIENTATION = True

#Base extensions for thumbnail files
EXTENSIONS = {
    'JPEG': 'jpg',
    'PNG': 'png',
    'BMP': 'bmp'
}
