#!/usr/bin/python3
'''
make QR code with logo (icon) in the middle
'''
import math, sys, os, logging  # pylint: disable=multiple-imports
from lxml import etree
import pyqrcode
logging.basicConfig(level=logging.DEBUG if __debug__ else logging.INFO)

BLOCKSIZE = 10
RADIUS = BLOCKSIZE * 4

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
    svg = document.xpath('//*[local-name()="svg"]')[0]
    logging.debug('svg: %s', svg)
    return svg

def touches_bounds(center, x, y, radius=RADIUS, block_size=BLOCKSIZE):
    '''
    make sure point (x, y) is in the empty space of the QR code
    '''
    scaled_center = center / block_size
    dis = distance((scaled_center , scaled_center), (x, y))
    rad = radius / block_size
    return dis <= rad + 1

def qr_code_with_logo(logo_path, url, outfile_name=None):
    '''
    generate QR code with logo included
    '''
    # pylint: disable=consider-using-f-string, c-extension-no-member
    if os.path.exists(url):
        with open(url, encoding='utf-8') as infile:
            url = infile.read().rstrip()
    if outfile_name is None:
        outfile_name = os.path.splitext(logo_path)[0] + '-qrcode.svg'
    logging.debug('generating QR code logo file "%s" and url "%s"',
                  logo_path, url)
    qr_code = generate_qr_code(url)
    image_size = str(qr_code.size[0] * BLOCKSIZE)
    logo_qr_code = newtree(image_size)
    pixels = qr_code.load()
    center = qr_code.size[0] * BLOCKSIZE / 2
    for x_position in range(0, qr_code.size[0]):
        for y_position in range(0, qr_code.size[1]):
            color = pixels[x_position, y_position]
            if color == (0,0,0,255):
                within_bounds = not touches_bounds(
                    center,
                    x_position,
                    y_position,
                    RADIUS,
                    BLOCKSIZE
                )
                if within_bounds:
                    etree.SubElement(
                        logo_qr_code,
                        'rect',
                        x=str(x_position*BLOCKSIZE),
                        y=str(y_position*BLOCKSIZE),
                        width='10',
                        height='10',
                        fill='black'
                    )
    logo = get_svg_content(logo_path)
    test = str(logo.get("viewBox"))
    array = []
    if test != "None":
        array = test.split(" ")
        width = float(array[2])
        height = float(array[3])
    else :
        width = float(str(logo.get("width")).replace("px", ""))
        height = float(str(logo.get("height")).replace("px", ""))
    scale = RADIUS * 2.0 / width
    scale_str = 'scale(%s)' % scale
    x_translate = ((qr_code.size[0] * BLOCKSIZE) - (width * scale)) / 2.0
    y_translate = ((qr_code.size[1] * BLOCKSIZE) - (height * scale)) / 2.0
    translate = 'translate(%s %s)' % (x_translate, y_translate)
    logo_scale_container = etree.SubElement(
        logo_qr_code,
        'g',
        transform=translate + " " + scale_str
    )
    for element in logo.getchildren():
        logo_scale_container.append(element)
    write_out(outfile_name, logo_qr_code)

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
        width=size,
        height=size,
        version='1.1',
        xmlns='http://www.w3.org/2000/svg'
    )

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        qr_code_with_logo(*sys.argv[1:])
    else:
        logging.error(
            'usage: %s octocat.svg "https://github.com/" [github-qrcode.svg]',
            sys.argv[0]
        )
