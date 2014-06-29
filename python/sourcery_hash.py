"""
A thing to demonstrate making hash-source directives for static files in CSP
"""
from base64 import b64encode
import hashlib
import sys
import html5lib
import getopt

hashers = {
        'sha256':hashlib.sha256,
        'sha384':hashlib.sha384,
        'sha512':hashlib.sha512
        }

def makeHashSource(alg, scr):
    hasher = hashers[alg]()
    hasher.update(scr)
    return alg+'-'+b64encode(hasher.digest())

def getScripts(doc):
    scripts = []
    document = html5lib.parse(doc)
    for script in document.iter('{http://www.w3.org/1999/xhtml}script'):
        scripts.append(script.text)
    return scripts

def getStyles(doc):
    styles = []
    document = html5lib.parse(doc)
    for style in document.iter('{http://www.w3.org/1999/xhtml}style'):
        styles.append(style.text)
    return styles

def makeHashSources(alg, doc, hash_scripts, hash_styles):
    script_sources = []
    style_sources = []

    script_bodies = getScripts(doc)
    style_bodies = getStyles(doc)

    if hash_scripts:
        for script in script_bodies:
            script_sources.append(makeHashSource(alg, script))
    if hash_styles:
        for style in style_bodies:
            style_sources.append(makeHashSource(alg, style))

    return script_sources, style_sources

if __name__ == '__main__':
    script_sources = []
    style_sources = []

    options, files = getopt.getopt(sys.argv[1:],'',['scripts','styles'])

    hash_scripts = False
    hash_styles = False

    for opt, val in options:
        if '--scripts' == opt:
            hash_scripts = True
        if '--styles' == opt:
            hash_styles = True

    for f in files:
        html = ''
        if len(sys.argv) > 1:
            html = open(f).read()

        script_sources, style_sources =  makeHashSources('sha256', html, hash_scripts, hash_styles)

    f = open('dot_htaccess','w')
    f.write('Header always set Content-Security-Policy "default-src \'self\'')
    if len(script_sources) > 0:
        f.write('; script-src')
        for source in script_sources:
            f.write(" '"+source+"'")
    if len(style_sources) > 0:
        f.write('; style-src')
        for source in style_sources:
            f.write(" '"+source+"'")
    f.write('"')
