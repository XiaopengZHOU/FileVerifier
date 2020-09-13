#!/usr/bin/python

from enum import Enum
class OutputStyle(Enum):
    Default = 0
    Legacy = 1

def main():
    from sys import argv
    ret, output_style, work_directory = parse_command_line_options(argv)
    if 0 != ret:
        exit(ret)

    verify_files(current_directory = work_directory,
        output_style = output_style)

def parse_command_line_options(arg_vector):
    output_style = OutputStyle.Default
    work_directory = None

    from getopt import error
    try:
        from getopt import getopt
        opts, argv = getopt(arg_vector[1:], "s:w:")
        for k, v in opts:
            if "-s" == k:
                if "legacy" == v.lower():
                    output_style = OutputStyle.Legacy
                elif "default" == v.lower():
                    output_style = OutputStyle.Default
                else:
                    show_usage()

                    from sys import stderr
                    print("Unknown output style \"%s\"" % v, file=stderr)

                    return 2, output_style, work_directory

            elif "-w" == k:
                from os.path import isdir
                if not isdir(v):
                    show_usage()

                    from sys import stderr
                    print("Directory not found for option \"-w '%s'\"" % v,
                        file=stderr)

                    return 2, output_style, work_directory
                else:
                    work_directory = v

    except error as msg:
        show_usage()

        from sys import stderr
        print(msg, file=stderr)

        return 1, output_style, work_directory

    if work_directory is None:
        from os import getcwd
        work_directory = getcwd()

    #print("WorkDirectory: \"%s\"" % work_directory)

    return 0, output_style, work_directory

def show_usage():
    print("Usage: ./file_verifier.py -s <default | legacy> -w <work-dir>\n")

def sum_from_file_CRC32(filename):
    from zlib import crc32
    with open(filename, "rb") as fh:
        hash = 0
        while True:
            s = fh.read(65536)
            if not s:
                break
            hash = crc32(s, hash)

        return "%08X" % (hash & 0xFFFFFFFF)

def verify_files(current_directory, output_style):
    from os import listdir
    items = listdir(current_directory)

    for item in items:
        # if item.startswith("."):
        #     continue

        from os.path import join
        fullpath = join(current_directory, item)

        #print("FullPath: \"%s\"" % fullpath)

        from os import stat
        st_mode = stat(fullpath).st_mode

        from stat import S_ISDIR, S_ISLNK, S_ISREG
        if S_ISDIR(st_mode):
            verify_files(current_directory = fullpath,
                output_style = output_style)
        elif S_ISREG(st_mode):
            if OutputStyle.Legacy == output_style:
                print("%s 0x%s" % (item, sum_from_file_CRC32(fullpath)))
            else:
                print("%s %s" % (fullpath, sum_from_file_CRC32(fullpath)))

if __name__ == "__main__":
    main()
