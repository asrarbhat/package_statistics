# top 10 debian packages that have most number of files associated

## problem statement

Debian uses *deb packages to deploy and upgrade software. The packages are stored in repositories and each repository contains the so called "Contents index". The format of that file is well described here <https://wiki.debian.org/RepositoryFormat#A.22Contents.22_indices>

Your task is to develop a python command line tool that takes the architecture (amd64, arm64, mips etc.) as an argument and downloads the compressed Contents file associated with it from a Debian mirror. The program should parse the file and output the statistics of the top 10 packages that have the most files associated with them. An example output could be:

    ./package_statistics.py amd64

    <package name 1>         <number of files>
    <package name 2>         <number of files>
    ...
    <package name 10>         <number of files> 
You can use the following Debian mirror: <http://ftp.uk.debian.org/debian/dists/stable/main/>. Please try to follow Python's best practices in your solution. Hint: there are tools that can help you verify your code is compliant. In-line comments are appreciated.

## my understanding of problem

write a python program that takes a command line argument(the architecture),and download Contents index file for thattop architecture and that file contains data regarding files and the package they are associated with. find top 10 most frequent packages, and print output containing top 10 packages and number of files assoicated with that packages in decending order.

# Approach/algorithm/thought process

## preprocessing

1. to make usage convenient,the whole program should be just one file.
1. verify the command entered
    - appropriate number of arguments given.
    - arguments are valid.
    - if error occurs,terminate gracefully with error message as specific as possible.
1. get the file from web
    - use requests module to send HTTP get request.
    - if error while getting the file from web,terminate gracefully,showing error code as output.
1. store the file in temporary file
    - since the file is compressed,to decompress it we would need whole file at once.
    - use tempfile module to create a temporary file which is removed automatically once program terminates.
1. unzip the file
    - use gzip module to unzip file into the temporary file created.
1. read the text in file
    - read the text in file for processing stage.

## processing

the data in file is stored in format as below:

\<filename\>\<one or more spaces\>\<packages separated by comma\>  

```
bin/afio                                                utils/afio
bin/bash                                                shells/bash
bin/bash-static                                         shells/bash-static
bin/brltty                                              admin/brltty
bin/bsd-csh                                             shells/csh
bin/btrfs                                               admin/btrfs-progs
bin/btrfs-convert                                       admin/btrfs-progs
bin/btrfs-find-root                                     admin/btrfs-progs
bin/btrfs-image                                         admin/btrfs-progs
bin/btrfs-map-logical                                   admin/btrfs-progs
bin/btrfs-select-super                                  admin/btrfs-prog
```

## optimizing text size

- since for each file the packages that it is associated with is mentioned on right side. We can get rid of filenames as from package names let alone we can find the frequency,hence we get rid of filenames and keep a list of strings,where each string is a package name.

## get frequency of all packages

- take the list contain package names and convert it into a dictionary with key being package name and value is the frequency of it in list.

## find top 10 most frequent pakcages and print them

- iterating 10 times over the dictioary is O(n) and is not that expensive computationally.

## other optimization suggestions

- although even with single thread downloading the file over a network is the bottleneck and not the parsing part.

  - eg it takes 20 seconds to download amd64 file and less than 3 seconds to process it and print output.

- but still with multithreading the processing part can be brought down to less than a second for the above example.

- i couldn't find a way to directly read a downloaded compressed data without saving it in a temporary file, however directly unzipping it without storing in a file increase memory usage.

- sometimes the file can get big eg when the argument is source ,we can use streaming to avoid running out of memory.

## timeline

- took me 20 minutes to wrap my head around the problem statement and understnad properly,what the given problem means.
- created a dummy solution in around 40 minutes that was working.

- spent around 4 hours(not at once) to make code readable and document the methods,module,class etc and also optimize the code for a single threaded program.

## code

```python

#!/usr/bin/python3

"""
NAME:
    packakage_statistics

DESCRIPTION:
    this module provides PackageStatistics class,that can be used to find top k
    packages with most number of files associated in a .deb repository.
    it uses Content file of a given repository to do so.

CLASSES:
    PackageStatistics(content_file_url,top_k)
        methods:
            execute(): to print output
    
"""

import requests  # to get data from web
import tempfile  # to create temporary file for storing downloaded data temporarily
import gzip  # to unzip the file
from sys import argv, exit  # to take command line arguments and exit if error occurs


class PackageStatistics:
    '''
    this class can find top k packages with most number of files
    associated in a content file of a .deb repository.

        public methods:

            execute():
                execute command and print output

        private attributes:

            __file_url: url of content file.
            __top_k : the size of output. 
            __file : object to store and tranform data.

        private methods:

            __get_file():
                get the content file from web

            __process_file()
                convert content file into dict with key=package name,value=number of files associated.

            __find()
                find k packages with highest number of files associated.

            __print()
                print output.


    '''

    def __init__(self, file_url, top_k=10):
        """
        paremeters:
            file_url -> str: the url of content file.
            top_k -> int   : the size of output (default 10).
        """

        self.__file_url = file_url
        self.__top_k = top_k

    def execute(self):
        """print output"""

        # private methods to be called in this order only.
        self.__get_file()
        self.__process_file()
        self.__find()
        self.__print()

    def __get_file(self):
        """ get the Content file of the repository. """

        try:
            # create a temporary file to store data to be downloaded from web.
            temporary_file = tempfile.NamedTemporaryFile()
        except:
            print(
                "[ERROR] unable to create a temporary file to store data to be downloaded!")
            # try again error
            exit(11)
        try:
            # get file from web
            content_file = requests.get(self.__file_url)
            if content_file.status_code != 200:
                print(content_file.status_code)
                raise Exception()
            content_file = content_file.content
        except:
            print("[ERROR] unable to get Content file from web!")
            exit(11)
        try:
            # store downloaded content file in a local temporary file
            temporary_file.write(content_file)

            # to free up space as file is stored in temporary_file
            del content_file
        except:
            print("[ERROR] unable to write to local temporary file!")
            exit(11)
        try:
            # unzip file and store as list of lines
            self.__file = gzip.open(temporary_file.name, "rt").readlines()
        except:
            print("[ERROR] unable to open the .gz file! ")

            # I/O error
            exit(5)

        finally:
            try:
                temporary_file.close()
            except:
                pass

    def __process_file(self):
        """create a dict, key=package name ,value= no of files associated"""

        # extract package names from a line in file and discard everything else
        def clean_line(line):
            if len(line.strip()) == 0:
                return "empty_line"
            # tranformation   "filename    pack1,pack2" =>  [pack1,pack2]
            return line.split(" ")[-1].strip().split(",")

        # tranformation : ["filename  pack1,pack2","filename pack3 pack4"....] => [[pack1,pack2],[pack3,pack4]...]
        self.__file = list(map(clean_line, self.__file))

        # to save memory while transforming data : instead of copying,remove from one and add to another.

        temp_data = []
        file_length = len(self.__file)

        # transformation : [[pack1,pack2],[pack3,pack4]] => [pack1,pack2,pack3,pack4]
        for i in range(file_length):
            temp_data.extend(self.__file.pop())

        # build a dict of packages and number of files associated.
        self.__file = {}
        temp_length = len(temp_data)
        for j in range(temp_length):
            package = temp_data.pop()
            self.__file[package] = self.__file.get(package, 0)+1

    def __find(self):
        """
        find top k packages with higest number of files associated,
         and store in self.__top_k_packages as list of list.
        """

        self.__top_k_packages = []  # [[pack1,n1],.....,[packk,nk]]

        # find package with maximum no of files associated  __top_k times
        for i in range(self.__top_k):
            max_file_count = 0
            package_name = ""
            for package, no_of_files in self.__file.items():
                if no_of_files > max_file_count:
                    package_name, max_file_count = package, no_of_files

            self.__top_k_packages.append([package_name, max_file_count])

            # to not find same package again
            self.__file[package_name] = 0

    def __print(self):
        """print top k packages with highest number of files associated"""

        # constant line length for each output line,to format output better.
        LINE_LENGHT = 50
        print()
        for package in self.__top_k_packages:
            package_name, number_of_files_associated = package[0], package[1]
            print(package_name, " "*abs(LINE_LENGHT -
                  len(package_name+str(number_of_files_associated))), number_of_files_associated)
        print()


if __name__ == "__main__":

    def validate_command() -> str:
        """validate the command and return the url of Content file."""

        arguments = argv[1:]
        arguments_length = len(arguments)

        # format of Content file path-> dists/$DIST/$COMP/Contents-$SARCH.gz
        file_url_format = "http://ftp.uk.debian.org/debian/dists/stable/main/Contents-<architecture>.gz"

        if arguments_length == 1 and arguments[0].strip().lower() != "help":
            file_url = file_url_format.replace(
                "<architecture>", arguments[0].strip())
            return file_url

        # take two arguments,where second one is url of Content file
        elif arguments_length == 2:
            file_url = arguments[1]
            return file_url

        # invalid command
        else:
            error = f'''
[   accepted format for commands   ] :

            {argv[0]} architecture
            example ->  {argv[0]} amd64

            {argv[0]} architecture Contents_index_url
            example ->  {argv[0]} amd64 http://ftp.uk.debian.org/debian/dists/stable/main/Contents-amd64.gz
            '''
            print(error)

            # invalid argument error
            exit(22)

    file_url = validate_command()
    job = PackageStatistics(file_url, top_k=10)
    job.execute()

```
