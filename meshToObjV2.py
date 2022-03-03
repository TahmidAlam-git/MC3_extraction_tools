#!/usr/bin/python3
import os
import sys
import math
import struct


def get_all_names(file_pointer) -> list:
    """ Get all the names found in the binary file

    Returns:
        List with structure of
        - [(name1, offset)]
            - offset/pointer position points to the start of the header
    """

    name_start_HEX = b'\x76\x72\x6F\x6F\x74' # "vroot"
    name_end_HEX = b'\x6D\x65\x73\x68\x00' # "mesh."
    names = []

    prev_pointer = 0
    while 1:
        # Find the model name start
        file_pointer.seek(0)
        name_start = file_pointer.read().find(name_start_HEX, prev_pointer)
        if name_start < 0:
            break

        # Find the end of the model name
        file_pointer.seek(0)
        name_end = file_pointer.read().find(name_end_HEX, prev_pointer)
        if name_end < name_start:
            break
        name_end += len(name_end_HEX) - 1

        # Get the name of the model
        file_pointer.seek(name_start)
        name = file_pointer.read(name_end - name_start).decode('utf-8')

        skip_to_next_line(file_pointer)

        names.append((name, file_pointer.tell()))
        prev_pointer = name_end
    return names


def byte_to_int(bytes) -> int:
    return int.from_bytes(bytes, byteorder='little')


def align_file_pointer(file_pointer) -> None:
    """ Set the file pointer at the start of the next line(16 bytes per line) """
    if file_pointer.tell() % 16 != 0:
        file_pointer.read(16 - (file_pointer.tell() % 16))


def skip_to_next_line(file_pointer) -> None:
    """ Sets the file pointer to the next line """
    file_pointer.read(1)
    align_file_pointer(file_pointer)


def read_main_header(file_pointer) -> tuple:
    """ Get the padding, face sections, and ff sections

    The model faces aren't all in continuous order, they are split up into
    their own sections as a part of the model.
    The file pointer will align to the next line.

    Returns: tuple
    """
    file_pointer.read(7)
    padding = byte_to_int(file_pointer.read(1)) - 12
    face_sections = byte_to_int(file_pointer.read(2))
    ff_sections = byte_to_int(file_pointer.read(2))
    align_file_pointer(file_pointer)

    # skip unknown line
    skip_to_next_line(file_pointer)

    # skip the 'face_section' number of shorts
    file_pointer.read(face_sections * 2)
    align_file_pointer(file_pointer)

    ''' skipping the filler is comprised of a 2 byte number specifying how many
    'sets' of filler there are, followed by 2 more bytes then the sets. These 
    sets are 22 bytes + 2 bytes of CD '''
    set_sections = byte_to_int(file_pointer.read(2))
    file_pointer.read(2)
    file_pointer.read(set_sections * (22 + 2))

    file_pointer.read(4 * 3)
    align_file_pointer(file_pointer)

    return (padding, face_sections, ff_sections)

def get_vertices_and_uv(file_pointer) -> tuple:
    """ Get the vertices, UVAs & UVBs
    Returns:
        tuple with structure of
        Index[0]: list of vertices i.e. [(X,Y,Z), (X2,Y2,Z2)]
        Index[1]: list of UVs i.e. [(UVA1, UVB1),(UVA2, UVB2)]
    """
    pass

def main():
    path = sys.argv[1]
    file_pointer = open(path, 'rb')

    names = get_all_names(file_pointer)
    name = names[0][0]
    offset = names[0][1]

    file_pointer.seek(offset)
    padding, face_sections, ff_sections = read_main_header(file_pointer)

    print(file_pointer.read(10).hex())





main()
