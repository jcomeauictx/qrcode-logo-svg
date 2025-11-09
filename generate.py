#!/usr/bin/python3
'''
make QR code with logo (icon) in the middle
'''
from __future__ import print_function, division
import math, sys, os, logging  # pylint: disable=multiple-imports
from tempfile import gettempdir
from xml.etree import ElementTree as etree
import pyqrcode
logging.basicConfig(level=logging.DEBUG if __debug__ else logging.INFO)

BLOCKSIZE = 10
RADIUS = BLOCKSIZE * 4
OPAQUE = 255
BLACK = (0, 0, 0, OPAQUE)
# python2 compatibility
try:
    with open(sys.argv[0], encoding='utf-8') as test:
        ENCODING={'encoding': 'utf-8'}
except TypeError:
    ENCODING={}

def distance(p0, p1):
    '''
    distance between two points
    '''
    result = math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)
    logging.debug('distance between %r and %r: %s', p0, p1, result)
    return result

def generate_qr_code(url):
    '''
    get "raw" QR code for URL, to which we will later add the logo (icon)
    '''
    logging.debug('generating QR code for "%s" without icon', url)
    qr_image = pyqrcode.MakeQRImage(
        url,
        errorCorrectLevel=pyqrcode.QRErrorCorrectLevel.H,
        block_in_pixels=1,
        border_in_blocks=0
    )
    return qr_image

def get_svg_content(filename):
    '''
    root may be the svg element itself, so search from tree

    solution for multiple (or no) namespaces from
    http://stackoverflow.com/a/14552559/493161
    '''
    # pylint: disable=c-extension-no-member
    document = etree.parse(filename)
    logging.debug('document: %s', document)
    svg = document.find('svg') or document.getroot()
    logging.debug('svg: %s', svg)
    return svg

def touches_bounds(center, x, y, radius=RADIUS, blocksize=BLOCKSIZE):
    '''
    make sure point (x, y) is in the empty space of the QR code
    '''
    scaled_center = center / blocksize
    dis = distance((scaled_center , scaled_center), (x, y))
    rad = radius / blocksize
    return dis <= rad + 1

def write_out(filename, tree):
    '''
    ElementTree 1.2 doesn't write the SVG file header errata,
    so do that manually
    '''
    # pylint: disable=c-extension-no-member
    with open(filename, 'wb') as outfile:
        outfile.write(b'<?xml version="1.0" standalone="no"?>\n')
        outfile.write(b'<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"\n')
        outfile.write(b'"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n')
        outfile.write(etree.tostring(tree))

def newtree(size):
    '''
    create an SVG XML element (see the SVG specification for attribute details)
    to house the combined URL QR code and the logo in the middle
    '''
    # pylint: disable=c-extension-no-member
    return etree.Element(
        'svg',
        width=str(size),
        height=str(size),
        version='1.1',
        xmlns='http://www.w3.org/2000/svg'
    )

def image_to_svg(image, blocksize=BLOCKSIZE, radius=RADIUS,
        for_logo=True):
    # pylint: disable=consider-using-f-string
    '''
    convert image to SVG file, optionally leaving room in the center
    '''
    # pylint: disable=c-extension-no-member
    x_size, y_size = image.size
    if x_size != y_size:
        raise ValueError('QR code not square: x=%s, y=%s' % (x_size, y_size))
    pixel_size = x_size * blocksize
    pixels = image.load()
    qrcode = newtree(pixel_size)
    center = x_size * blocksize / 2
    logging.debug("qr_code.size: %s, center: %s", pixel_size, center)
    for x_position in range(0, x_size):
        for y_position in range(0, y_size):
            color = pixels[x_position, y_position]
            if color == BLACK:
                within_bounds = not touches_bounds(
                    center,
                    x_position,
                    y_position,
                    radius,
                    blocksize
                )
                if within_bounds or not for_logo:
                    etree.SubElement(
                        qrcode,
                        'rect',
                        x=str(x_position*blocksize),
                        y=str(y_position*blocksize),
                        width='10',
                        height='10',
                        fill='black'
                    )
    return qrcode

def get_viewbox(logo):
    '''
    return x offset, y offset, width, and height of image
    '''
    view_box = str(logo.get("viewBox"))
    logging.debug('view_box from logo["view_box"]: %s', view_box)
    if view_box != "None":
        view_box = tuple(map(float, view_box.split(" ")))
    else :
        width = float(logo.get("width").replace("px", ""))
        height = float(logo.get("height").replace("px", ""))
        view_box = (0, 0, width, height)
    logging.debug('final view_box: %r', view_box)
    return view_box

def paste_logo(qr_code, logo_path, blocksize=BLOCKSIZE, radius=RADIUS):
    '''
    paste logo into middle of logo_qr_code
    '''
    # pylint: disable=c-extension-no-member, consider-using-f-string
    logo_qr_code = image_to_svg(qr_code)
    logo = get_svg_content(logo_path)
    x_offset, y_offset, width, height = get_viewbox(logo)
    logging.debug('x_offset=%s, y_offset=%s, width=%s, height=%s',
                  x_offset, y_offset, width, height)
    scale = radius * 2.0 / width
    transform = 'translate(%s %s)' % (
        ((qr_code.size[0] * blocksize) - (width * scale)) / 2.0,
        ((qr_code.size[1] * blocksize) - (height * scale)) / 2.0
    )
    transform += ' scale(%s)' % scale
    logging.debug('transform: %s', transform)
    logo_scale_container = etree.SubElement(
        logo_qr_code,
        'g',
        transform=transform
    )
    logging.debug('logo subelements: %s', logo.find('.'))
    for element in logo.find('.'):
        logo_scale_container.append(element)
    return logo_qr_code

def qr_code_with_logo(logo_path, url, outfile_name=None, blocksize=BLOCKSIZE,
        radius=RADIUS):
    '''
    generate QR code with logo included
    '''
    # pylint: disable=consider-using-f-string, c-extension-no-member
    directory, filename = os.path.split(logo_path)
    file_prefix = os.path.splitext(filename)[0]
    if os.path.exists(url):
        with open(url, **ENCODING) as infile:
            url = infile.read().rstrip()
    if not outfile_name:
        outfile_name = os.path.join(directory, file_prefix + '-qrcode.svg')
    logging.debug('generating QR code logo file "%s" and url "%s"',
                  logo_path, url)
    qr_code = generate_qr_code(url)
    if __debug__:
        write_out(
            os.path.join(
                gettempdir(),
                file_prefix + '-qrcode-plain.svg'
            ),
            image_to_svg(qr_code, blocksize, radius, for_logo=False)
        )
    logo_qr_code = paste_logo(qr_code, logo_path, blocksize, radius)
    write_out(outfile_name, logo_qr_code)

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        qr_code_with_logo(*sys.argv[1:])
    else:
        logging.error(
            'usage: %s octocat.svg "https://github.com/" [github-qrcode.svg]',
            sys.argv[0]
        )
