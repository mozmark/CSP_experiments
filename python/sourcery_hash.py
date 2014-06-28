"""
A thing to demonstrate making hash-source directives for static files in CSP
"""
from base64 import b64encode
import hashlib
import sys
import html5lib

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

def makeHashSources(alg, doc):
    sources = []
    script_bodies = []

    script_bodies = getScripts(doc)

    for script in script_bodies:
        sources.append(makeHashSource(alg, script))
    return sources

if __name__ == '__main__':
    sources = []

    files = sys.argv[1:]
    for f in files:
        html = ''
        if len(sys.argv) > 1:
            html = open(f).read()

        for source in makeHashSources('sha256',html):
            sources.append(source)

    f = open('dot_htaccess','w')
    f.write('Header always set Content-Security-Policy "default-src \'self\'; script-src')
    for source in sources:
        f.write(" '"+source+"'")
    f.write('"')
