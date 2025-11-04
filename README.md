#QR Code SVG Logo Generator
==========================
generate QR codes with your logo in the middle.

![example code](http://ddrboxman.github.com/QR-Code-SVG-Logo-Generator/sample.png)

logo should be a svg file, the output QR code is also an SVG

simply pass the svg file containing the logo, the url you want on the QR code, and the output filename

```
./generate.py octocat.svg "https://github.com/" octocatqr.svg
```

alternatively, make .svg and .link files for each QR code you want to generate
in this directory, and simple `make` to build them. the resulting svg file
will be of the form [PREFIX]-qrcode.svg.

## dependencies
------------
Python modules:

PIL (Python Imaging Library)

## attributions
* [Pi logo](https://seeklogo.com/vector-logo/440686/pi-network-lvquy)
* [Monero logo](https://cryptologos.cc/monero)
* [Bitcoin Cash logo](https://bitcoincash.org/graphics/)
* [PayPal logo](https://commons.wikimedia.org/wiki/File:PayPal_Logo_Icon_2014.svg) (public domain)
* [PayPal payment URL instructions](https://www.labnol.org/paypal-payment-email-documents-5983)
