# USAGE
---
## URL Input
### 1. File containing text to parse for valid URLs
    [--input], [-i] filepath
### 2. URLs as strings, space separated
    [--urls], [-u] test.com/file1.txt test.com/file2.txt
---
## Directory Output
### Parent subdirectory for all downloads, defaults to cwd
    [--dirprefix], [-d] downloadfolder/

### Autosort options:
#### 1. Mirror directory structure of netpath for each url
    [--hostsort]
#### 2. Organize [and create] directories based on file types
    [--typesort]
#### 3. Organize [and create] directories based on shared file names - Not implemented
    [--namesort]

---
## Write Options
### Skip download and print parsed URLs to stdout
    [--extract], [-x]
### Overwrite existing files of same name
    [--overwrite]
### Skip specified filetypes
    [--reject], [-r] pdf .txt
### Write / append details to download log file
CSV text format is date, time, url, filepath

    [--log], [-l] downloadfolder/logfile.csv
