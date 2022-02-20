#!/usr/bin/python3

"""
NAME:
    packakage_statistics

DESCRIPTION:
    this module provides PackageStatistics class,that can be used to find top K
    packages with most number of files associated in a .deb repository.
    it uses Contents index file of the given repository to do so.

CLASSES:
    PackageStatistics(content_file_url,top_k)
        public methods:
            execute(): to print output
    
"""

import requests  # to get file from web
import tempfile  # to create a temporary file to store downloaded data temporarily
import gzip  # to unzip the file
from sys import argv, exit  # to take command line arguments and exit if error occurs


class PackageStatistics:
    '''
    the objects of this class can find top k packages in a .deb repository with most number of files
    associated, using the contents file of a .deb repository.

        public methods:

            execute():
                execute command and print output

        private attributes:

            __file_url: url of Contents index file.
            __top_k : number of packages to be printed as output. 
            __file : object to store and tranform data.

        private methods:

            __get_file():
                get the Contents index file from web

            __process_file()
                convert Contents file into dict with key=package name,value=number of files associated.

            __find()
                find __top_k packages with highest number of files associated.

            __print()
                print output.


    '''

    def __init__(self, file_url, top_k=10):
        """
        paremeters:
            file_url -> str: the url of Content index file.
            top_k -> int   : the size of output (default 10).
        """

        self.__file_url = file_url
        self.__top_k = top_k

    def execute(self):
        """print output"""

        # private methods to be called in this order only.
        self.__get_file()
        self.__process_file()
        self.__find_packages()
        self.__print()

    def __get_file(self):
        """ get the Contents index file of the repository. """

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
            contents_file = requests.get(self.__file_url)
            if contents_file.status_code != 200:  # 200 means OK / success
                print(contents_file.status_code)
                raise Exception()
            contents_file = contents_file.content
        except:
            print("[ERROR] unable to get Content file from web!")
            exit(11)
        try:
            # store downloaded content file in a local temporary file
            temporary_file.write(contents_file)

            # to free up space as file is stored in temporary_file
            del contents_file
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
                return ["empty_line"]

            # tranformation :   "filename    pack1,pack2" =>  ["pack1","pack2"]
            return line.split(" ")[-1].strip().split(",")

        # tranformation : ["filename  pack1,pack2","filename pack3 pack4"....] => [["pack1","pack2"],["pack3","pack4"]...]
        self.__file = list(map(clean_line, self.__file))

        # to save memory while transforming data : instead of copying,remove from one object and add to another.

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

    def __find_packages(self):
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
        """validate the command and return the url of Contents index file."""

        arguments = argv[1:]
        no_of_arguments = len(arguments)

        # format of Contents index file path-> dists/$DIST/$COMP/Contents-$SARCH.gz
        file_url_format = "http://ftp.uk.debian.org/debian/dists/stable/main/Contents-<architecture>.gz"

        if no_of_arguments == 1 and arguments[0].strip().lower() != "help":
            file_url = file_url_format.replace(
                "<architecture>", arguments[0].strip())
            return file_url

        # take two arguments,where second one is url of Content index file
        elif no_of_arguments == 2:
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
