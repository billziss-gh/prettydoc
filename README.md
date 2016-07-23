# Prettydoc - Produce Pretty Documentation

Prettydoc is a simple tool that I use to create Apple-like documentation.
You can see a working example [here](http://www.secfs.net/winfsp/apiref/).
Prettydoc can produce output in different formats: html, manpage, markdown.

Prettydoc is a wrapper around Apple's headerdoc.
The project includes a patched version of headerdoc as a submodule.
Headerdoc has a few dependencies and must be built before it can be used with prettydoc.

Headerdoc dependencies include the following (some of them may already be satisfied in your system):

* libxml2-dev
* HTML::Entities
* Tie::IxHash
* xmllint

Full instructions:

    $ git clone https://github.com/billziss-gh/prettydoc.git
    $ cd prettydoc
    $ git submodule update --init
    $ make -C headerdoc             # headerdoc is written in Perl and C
    $ tst/run-tests

Prettydoc runs on OSX, Linux and Windows/Cygwin.
