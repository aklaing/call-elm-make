#!/usr/bin/env python

########################################################################
# Configure these to the needs of your editor.  See helpString below for
# documentation.

useFullPaths = False
showLineNumbers=True
showColumnNumbers=True
showEndParameters=False
onNextLine=True
hideCodeSnippets=False

########################################################################

helpString = '''

This wrapper for elm-make displays the error line and column numbers,
in a format compatible with emacs' compilation mode.  With it, your
next-error function will work in a nice way.  For example, this
wrapper can display an error header as follows:

-- TYPE MISMATCH -----------------------------------------------------
Main.elm:76:14

There are six boolean parameters you can easily configure in the
script.  The example header above corresponds to the following
settings of the parameters.

useFullPaths = False      # Whether to not use relative paths
showLineNumbers=True      # Where the error begins
showColumnNumbers=True    # Where the error begins
showEndParameters=False   # Corresponding pair where the error ends
onNextLine=True           # Whether to insert a newline before the locus
hideCodeSnippets=False    # A more compact layout for error buffer eg. if
                          # you have the full code in a another visible 
                          # buffer anyway.

Your editor will need to either work with your chosen configuration
out of the box, or else you may need to tune your plugin
(eg. elm-mode's elm-interactive.el for emacs) by changing the regular
expression for matching a locus so that it matches the three pieces of
information (file, line, column) in one regular expression.  Detailed
instructions are provided on how to do this on.

http://github.com/aklaing/call-elm-make

To run the script, you need to have python installed, along with the
termcolor package.  Then invoke this script as follows inside emacs
(make it your compile-command, for example):

$ ./call-elm-make.py Main.elm

The script only controls the use of the --report=(json|normal)
parameter, so all other parameters you may provide are passed on to
elm-make.

LIMITATIONS

- The coloring that the elm-compiler does is lost, but a similar
coloring is reconstructed, which is close but not identical.

'''

########################################################################

from subprocess import Popen, PIPE
import sys
import os
import re
import json
from termcolor import colored

errors = []

def replaceMessageBar(mo):
    global errors
    global cwd
    e = errors.pop(0)
    e['tag']
    if e['tag'] != mo.group('tag') or e['file'] != mo.group('file'):
        # Error condition: Don't know what to do -- play it safe, no change.
        return mo.group(0)
    if 'subregion' in e:
        location = e['subregion']['start']
        endLocation = e['subregion']['end']
    else:
        location = e['region']['start']
        endLocation = e['region']['end']
    if useFullPaths:
        fileName = os.path.join(cwd, e['file'])
    else:
        fileName = e['file']
    lineNumber = ''
    columnNumber = ''
    endLineNumber = ''
    endColumnNumber = ''
    if showLineNumbers:
        lineNumber = ':' + str(location['line'])
    if showColumnNumbers:
        columnNumber = ':' + str(location['column'])
    if showEndParameters:
        if showLineNumbers:
            endLineNumber = ':' + str(endLocation['line'])
        if showColumnNumbers:
            endColumnNumber = ':' + str(endLocation['column'])
    if onNextLine:
        separator = '\n'
    else:
        separator = ' '
    return ''.join([
        '\n',
        '-- ',
        colored(e['tag'] + ' ' + mo.group('longline') + separator, 'cyan'),
        fileName,
        lineNumber,
        columnNumber,
        endLineNumber,
        endColumnNumber,
        ])


def replaceGreaterThan(mo):
    return mo.group('line') + '|' + colored(mo.group('greaterThan'), 'red') + mo.group('content') + '\n'

def replaceCarets(mo):
    return mo.group('prefix') + colored(mo.group('carets'), 'red') + '\n'

def replaceType(mo):
    return '\n' + mo.group('prefix') + colored(mo.group('content'), 'yellow') + '\n'

########################################################################
try:
    sys.argv.remove('--report=json')
    sys.argv.remove('--report=normal')
except:
    pass
if len(sys.argv) <= 1:
    print helpString
else:
    cwd = os.getcwd()
    p = Popen(["elm-make", "--report=json"] + sys.argv[1:], stdout=PIPE, stderr=PIPE)
    (jsonOut, jsonErr) = p.communicate()
    p2 = Popen(["elm-make"] + sys.argv[1:], stdout=PIPE, stderr=PIPE)
    (normOut, normErr) = p2.communicate()
    if p2.returncode == 0:
        print normOut
        sys.exit(0)
    else:
        errors = json.loads(jsonOut)
        normErr = re.sub(
            r'-- (?P<tag>[A-Z0-9_ ]+) (?P<longline>-+) (?P<file>.*\.[Ee][Ll][Mm])',
            replaceMessageBar,
            normErr)
        if hideCodeSnippets:
            normErr = re.sub(r'\d+[|]([>]?).*\n', '', normErr)
        else:
            normErr = re.sub(
                r'(?P<line>\d+)[|](?P<greaterThan>[>]?)(?P<content>.*)\n',
                replaceGreaterThan,
                normErr)
        if hideCodeSnippets:
            normErr = re.sub(r'([ ]+)([#^]+)\n', '', normErr)
        else:
            normErr = re.sub(
                r'(?P<prefix>[ ]+)(?P<carets>[!^]+)\n',
                replaceCarets,
                normErr)
        normErr = re.sub(
            r'\n(?P<prefix>[ \t]+)(?P<content>[^^].+)\n',
            replaceType,
            normErr)
        print normErr
        sys.exit(1)
