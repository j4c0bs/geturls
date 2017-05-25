# USAGE
-------

URL Input
---------

1. File(s) containing text to parse for valid URLs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    [--input], [-i] filepath

2. URLs as strings, space separated
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[--urls], [-u] test.com/file1.txt test.com/file2.txt
----------------------------------------------------

Directory Output
----------------

Parent subdirectory for all downloads, defaults to cwd
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    [--dirprefix], [-d] downloadfolder/

Autosort options:
-----------------

1. Mirror directory structure of netpath for each url
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    [--hostsort]

2. Organize files [and create directories] based on file types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    [--typesort]

3. Organize files [and create directories] based on shared file names or matches to directory names in cwd
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    [--namesort]

+-----+
| ##  |
| Wri |
| te  |
| Opt |
| ion |
| s   |
| ### |
| Ove |
| rwr |
| ite |
| exi |
| sti |
| ng  |
| fil |
| es  |
| of  |
| sam |
| e   |
| nam |
| e   |
| [-- |
| ove |
| rwr |
| ite |
| ]   |
| ### |
| Ski |
| p   |
| spe |
| cif |
| ied |
| fil |
| ety |
| pes |
| [-- |
| rej |
| ect |
| ],  |
| [-r |
| ]   |
| pdf |
| .tx |
| t   |
| ### |
| Wri |
| te  |
| [ap |
| pen |
| d]  |
| det |
| ail |
| s   |
| to  |
| dow |
| nlo |
| ad  |
| log |
| fil |
| e   |
| CSV |
| tex |
| t   |
| for |
| mat |
| is  |
| dat |
| e,  |
| tim |
| e,  |
| url |
| ,   |
| fil |
| epa |
| th  |
+-----+
| [-- |
| log |
| ],  |
| [-l |
| ]   |
| dow |
| nlo |
| adf |
| old |
| er/ |
| log |
| fil |
| e.c |
| sv  |
+-----+

Display Options
---------------

Minimal, impermanent status display
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    [--quiet], [-q]

No status display or text printed to stdout
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    [--silent], [-s]

--------------

Other Options
-------------

Skip download and print parsed URLs to stdout
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    [--extract], [-x]

Wait n seconds in between sequential requests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    [--wait], [-w] n
