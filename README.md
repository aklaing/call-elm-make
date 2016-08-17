# call-elm-make

Provide support for `next-error` navigation with elm-compiler errors
in emacs.

It is implemented as a wrapper for **elm-make**, and it displays the
error line and column numbers, in a format compatible with **emacs**'
**compilation-mode**.  With it, the emacs `next-error` function will
more accurately navigate to the location of each elm-compiler error in
your source code.  For example, this wrapper can display an error
header as follows:

```
-- TYPE MISMATCH -----------------------------------------------------
Main.elm:76:14
```

There are six boolean parameters you can easily configure in the
script that control the output format.  The example header above
corresponds to the following settings of the parameters.

```python
useFullPaths=False        # Whether to not use relative paths
showLineNumbers=True      # Where the error begins
showColumnNumbers=True    # Where the error begins
showEndParameters=False   # Corresponding pair where the error ends
onNextLine=True           # Whether to insert a newline before the locus
hideCodeSnippets=False    # A more compact layout for error buffer eg. if
                          # you have the full code in a another visible 
                          # buffer anyway.
```

Your editor will need to either work with your chosen configuration
out of the box, or else you may need to tune your plugin
(eg. **elm-mode**'s file `elm-interactive.el` for **emacs**) by changing the
regular expression for matching a locus so that it matches the three
pieces of information (file, line, column) in one regular expression.
Detailed instructions are provided on how to do this below.

To run the script, you need to have **python** installed, along with
the **termcolor** package.  Then make the script executable, and
invoke it as follows inside emacs (make it your `compile-command`, for
example):

```
$ ./call-elm-make.py Main.elm
```

The script only controls the use of the `--report=(json|normal)`
parameter, so all other parameters you may provide are passed on to
elm-make.

## LIMITATIONS

- The coloring that the elm-compiler does is lost, but a similar
coloring is reconstructed, which is close but not identical.

## INSTALLING PYTHON AND TERMCOLOR

### On Ubuntu:

Something like this should work.  Google otherwise.

```
$ sudo apt-get install python
$ pip install termcolor
```

## HOW TO USE WITH EMACS

Please look for the file `elm-interactive.el` on your system.  It may
be located under a directory with a similar name to this:
`.emacs.d/elpa/elm-mode-20160605.201`.

In it, comment out the following lines (with semicolons :-)):

```elisp
(defvar elm-compile-error-regexp-alist-alist
   '((elm-file "-- [^-]+ -+ \\(.+\\)$" 1 nil)
     (elm-line "^\\([0-9]+\\)|" nil 1))
   "Regexps to match Elm compiler errors in compilation buffer.")

(defvar elm-compile-error-regexp-alist '(elm-line elm-file))
```

And insert the following lines:

```elisp
(defvar elm-compile-error-regexp-alist-alist
   '((elm-locus "-- [^-]+ -+ \\(.+\\):\\([0-9]+\\):\\([0-9]+\\)$" 1 2 3))
     "Regexp to match Elm compiler errors in compilation buffer.")

(defvar elm-compile-error-regexp-alist '(elm-locus))
```

Then run the emacs command `byte-compile-file`, save, and exit emacs.
Please let me know if any other steps are necessary for you, including
any changes to the regular expression.  If you use this particular
setting unmodified, you will need to set `onNextLine=False` in the
script.

# FAQ

### Why not support this natively in the elm-compiler and elm-make?

Using this script provides some flexible control which an end-user can
easily and quickly adjust to their own needs when necessary.

### Will this work with all editors?

I only know that it works with **emacs**.  I expect it to work with
any editor that is able to call an external compiler and then process
the compiler output by searching for error locations with regular
expressions.  Please let me know if this works for you in a different
editor -- that would be great!

### Why not implement this in emacs?  Why python?

Frankly, because my python run rings around my elisp, and having an
isolated tool could possibly benefit other editors, in one go.
Theoretically.

### How does it work?

It calls elm-make twice, and then processes the outputs with a json
library and python regular expressions, and then works from there.  It
is not robust in the sense that changes in elm's output formats could
break this tool.  It is not perfect even now because some assumptions
have been made about the elm-compiler's output formats which may not
hold in all cases.  However I hope it can be very useful immediately
and that it will only improve over time.

### But it doesn't work for me!

If your editor is able to call an external compiler and then process
the compiler output by searching for error locations with regular
expressions, maybe this tool can be modified to help your case.  If no
combination of the parameters above works well for you, a new feature
can fairly easily be added -- a configuration option which is a
template string, with which you can format your own header output.  I
don't think this will be necessary but it is not difficult to do.  It
would overrride all the boolean parameters mentioned above, and could
look something like this, for example:

```
useMyOwnFormat = Template('-- $tag at $fileName: ($lineNumber,$columnNumber) -- ($endLineNumber, $endColumnNumber) -----------'
```

It is a good idea however to retain as much as possible of elm's
artistic style and make only the minimum modifications that are
absolutely necessary to make it easy for an editor to interoperate.

### Is this officially supported?

No.  It is purely a use-at-your-own-risk proposition, and is not
endorsed by anyone, including myself.  Please see the included MIT
License.

