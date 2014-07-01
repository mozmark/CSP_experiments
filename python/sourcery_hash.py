"""
A thing to demonstrate making hash-source directives for static files in CSP
"""
from base64 import b64encode
import hashlib
import sys
import html5lib
import getopt

class CSP:
    directives = {}

    def __init__(self, policy_string):
        directive_strings = [ps.rstrip() for ps in policy_string.split(';')]
        for directive in directive_strings:
            if len(directive) > 0:
                name, value = directive.split(' ',1)
                self.directives[name] = value

    def append_source(self, directive, source):
        current_sources = ''
        try:
            current_sources = self.directives[directive]
        except:
            pass
        self.directives[directive] = current_sources + ' ' + source

    def tostring(self):
        return '; '.join([name+' '+self.directives[name] for name in self.directives.keys()])

hashers = {
        'sha256':hashlib.sha256,
        'sha384':hashlib.sha384,
        'sha512':hashlib.sha512
        }

def makeHashSource(alg, scr):
    hasher = hashers[alg]()
    hasher.update(scr)
    return "'%s-%s'"%(alg, b64encode(hasher.digest()))

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

    options, files = getopt.getopt(sys.argv[1:],'',['scripts','styles','existing='])

    hash_scripts = False
    hash_styles = False
    existing = ''

    for opt, val in options:
        if '--scripts' == opt:
            hash_scripts = True
        if '--styles' == opt:
            hash_styles = True
        if '--existing' == opt:
            existing = val

    policy = CSP(existing)

    for f in files:
        html = ''
        if len(sys.argv) > 1:
            html = open(f).read()

        script_sources, style_sources =  makeHashSources('sha256', html, hash_scripts, hash_styles)

    f = open('dot_htaccess','w')
    if len(script_sources) > 0:
        for source in script_sources:
            policy.append_source('script-src', source)
    if len(style_sources) > 0:
        for source in style_sources:
            policy.append_source('style-src', source)
    f.write("Header always set Content-Security-Policy \"%s\""%(policy.tostring()))
