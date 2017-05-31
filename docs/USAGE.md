# geturls usage:
---

Input URLs directly or via text file(s). Contents are parsed for possible URLs which are then normalized and downloaded. Failed requests are displayed after completion and sorting of successful requests.

Automatic file sorting options will fall back to cwd or parent subdirectory if a directory name is unavailable due to an existing file.

The namesort option finds matching tokens within incoming file names that are at least 3 characters in length. Name matching is prioritized by currently existing directory names in cwd. If no match is located, groups of matching file names are written to a directory named after the longest shared token (if it exists). Without a token match, a directory is created based on the file's name.

---
## URL Input - choose one:
#### 1. File(s) containing text to parse for valid URLs
    [--input], [-i] filepath
#### 2. URLs as strings, space separated
    [--urls], [-u] test.com/file1.txt test.com/file2.txt
---
## Directory Output
#### Parent subdirectory for all downloads, defaults to cwd
    [--dirprefix], [-d] downloadfolder/

## Autosort options - choose one:
#### 1. Mirror directory structure of netpath for each url
    [--hostsort]
#### 2. Organize files [and create directories] based on file types
    [--typesort]
#### 3. Organize files [and create directories] based on shared file names or matches to directory names in cwd
    [--namesort]

---
## Write Options
#### Overwrite existing files of same name
    [--overwrite]
#### Skip specified filetypes
    [--reject], [-r] pdf .txt
#### Write [append] details to download log file
CSV text format: date, time, url, filepath

    [--log], [-l] downloadfolder/logfile.csv

---
## Display Options
#### Minimal, impermanent status display
    [--quiet], [-q]
#### No status display or text printed to stdout
    [--silent], [-s]

---
## Other Options
#### Skip download and print parsed URLs to stdout
    [--extract], [-x]
#### Wait n seconds in between sequential requests
    [--wait], [-w] n
