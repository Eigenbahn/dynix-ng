# dynix-ng

`dynix-ng` aims at reproducing the user interface of the classic [Dynix Automated Library System](https://en.wikipedia.org/wiki/Dynix_(software)), certainly the most iconic text-based [ILS](https://en.wikipedia.org/wiki/Integrated_library_system).


## Running

#### conda

Installation:

    $ git clone https://github.com/Eigenbahn/dynix-ng
    $ cd dynix-ng
    $ conda env create

Running:

    $ conda activate dynix-ng-env
    $ python3 dynix_ng/__init__.py


## What works

Non blocking main menu implemented w/ [curses](https://docs.python.org/3/library/curses.html).


## What comes next

Basic integration with calibre db backend.


## What comes later

Integration w/ archive.org, worldcat.org, proper [OPAC](https://en.wikipedia.org/wiki/Online_public_access_catalog)s...

We expected to also integrate w/ [goodreads.com](https://www.goodreads.com/) but sadly they are starting to [close their public API](https://joealcorn.co.uk/blog/2020/goodreads-retiring-API).


## Author

Jordan Besly [@p3r7](https://github.com/p3r7) ([blog](https://www.eigenbahn.com/)).


## Similar projects

https://github.com/jonatanskogsfors/librix
