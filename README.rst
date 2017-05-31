geturls
=======

Pure Python command line package for parsing, downloading, and sorting URLs.
Features include automatic repair of URL syntax and multiple file sorting
options to keep your directories organized.

Installation
------------

::

    python setup.py install

Command Line Usage
------------------

See
`USAGE <https://github.com/j4c0bs/geturls/blob/master/docs/USAGE.md>`_
for expanded details.

To see a list of available arguments, run ''geturls --help''

::

    basic usage: geturls [--input] | [--urls]

    optional arguments:
      -h, --help            show this help message and exit

      --input, -i           Input file(s) to parse for URLs
      --urls, -u            Input text URL(s) to download

      --dirprefix, -d       Root / parent directory to store all files and
                            subdirectories. Defaults to cwd

      --hostsort            Create subdirectories based on host site
      --namesort            Create subdirectories based on filenames
      --typesort            Create subdirectories based on filetypes

      --extract, -x         Skip download and print URLs to stdout
      --overwrite           Overwrite existing files of same name
      --reject, -r          Skip filetypes entered
      --wait, -w            Seconds to wait in between url requests. Defaults to
                            0.01
      --quiet, -q           Minimal status display to stdout
      --silent, -s          Disable all printing to stdout
      --log, -l             Write / append to download log file

Requirements
------------

-  Python 3.4.3 or greater

License
-------

geturls is released under the BSD 2-clause license. See
`LICENSE <https://raw.githubusercontent.com/j4c0bs/geturls/master/LICENSE.txt>`_
for details.
