#!/usr/bin/python3
import os
import math
import struct


def convert(hfile, fname):

    '''
    example: vroot_bmpf_bone_bumpf_stk_350z_bumpf_stk_350z_geo.mesh.xbck
    nissan 350z stock front bumper mesh, beginning header

    header part 0
    always useless starting 8 lines
    00 9A 9E 82 16 00 00 00 01 00 00 00 B0 3F 00 00
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00

    header part 1
    70 B6 5D 00 00 00 71 1C 09 00 00 00 20 9A 9E 82
                            ^^ ^^ ^^ ^^
    how many numbers there are at the end of this part of the header(before the multi CD padding)
    This also means how many pieces the model is split up into (useful for faces)

    44 9A 9E 82 00 00 00 00 1C 9B 9E 82 E0 D2 9E 82 <= always skip
    17 00 05 00 05 00 14 00 18 00 01 00 13 00 05 00 <= 8 numbers here
    19 00 CD CD CD CD CD CD CD CD CD CD CD CD CD CD <= 1 number here, 9 total

    header part 2
    09 00 00 00 <= value represents how many "sets" there are

    sets are 24 bytes long, ends with CD CD
    70 D2 9E 82 C1 5E 80 00 59 00 1C 00 02 4A 04 00
    00 00 00 00 01 00 CD CD
    7C D2 9E 82 C1 5E 80 00 59 00 1C 00 02 4A 04 00
    00 00 00 00 01 00 CD CD
    88 D2 9E 82 C1 5E 80 00 59 00 1C 00 02 4A 04 00
    00 00 00 00 01 00 CD CD
    94 D2 9E 82 C1 5E 80 00 59 00 1C 00 02 4A 04 00
    00 00 00 00 01 00 CD CD
    A0 D2 9E 82 C1 5E 80 00 59 00 1C 00 02 4A 04 00
    00 00 00 00 01 00 CD CD
    AC D2 9E 82 C1 5E 80 00 59 00 1C 00 02 4A 04 00
    00 00 00 00 01 00 CD CD
    B8 D2 9E 82 C1 5E 80 00 59 00 1C 00 02 4A 04 00
    00 00 00 00 01 00 CD CD
    C4 D2 9E 82 C1 5E 80 00 59 00 1C 00 02 4A 04 00
    00 00 00 00 01 00 CD CD
    D0 D2 9E 82 C1 5E 80 00 59 00 1C 00 02 4A 04 00
    00 00 00 00 01 00 CD CD

    header part 3
    last part of header always ends with 4 00, + CD padding if neeeded
    01 00 00 00 30 9B 9E 02 00 00 00 00 CD CD CD CD CD CD CD CD
    '''


    l_len = 16

    # header part 1
    hfile.read(8)
    pieces = int.from_bytes(hfile.read(4), byteorder='little')
    hfile.read(4)
    hfile.read(l_len + math.ceil(pieces / 8) * l_len)

    # header part 2
    sets_num = int.from_bytes(hfile.read(4), byteorder='little')
    hfile.read(sets_num * 24)

    # header part 3
    hfile.read(12)
    if hfile.tell() % 16 != 0:
        hfile.read(16 - (hfile.tell() % 16))

    vertices = []
    faces = []
    UVs = []

    # TODO: find the amount of vertices from header
    # get the vertices and UVs
    while 1:
        x = struct.unpack('f', hfile.read(4))[0]
        y = struct.unpack('f', hfile.read(4))[0]
        z = struct.unpack('f', hfile.read(4))[0]

        if float(format(x, '.4f')) == float(format(y, '.4f')) == float(format(z, '.4f')) == 0.0000:
            hfile.seek(-12, 1)
            break

        vertices.append((x, y, z))

        hfile.read(8)

        uva = struct.unpack('f', hfile.read(4))[0]
        uvb = struct.unpack('f', hfile.read(4))[0]
        UVs.append((uva, uvb))


    '''
    faces header example
    the model is split up into multiple pieces
    
                                       offset + amount
    01 00 00 00 00 00 1E 00 00 00 00 00 : 000 + 030
    01 00 00 00 1E 00 97 00 00 00 00 00 : 030 + 151
    01 00 00 00 B5 00 68 00 00 00 00 00 : 181 + 104
    01 00 00 00 1D 01 90 00 00 00 00 00 : 285 + 144
    01 00 00 00 AD 01 13 00 00 00 00 00 : 429 + 019
    01 00 00 00 C0 01 40 01 00 00 00 00 : 448 + 320 
    01 00 00 00 00 03 1B 00 00 00 00 00 : 768 + 027
    01 00 00 00 1B 03 4E 01 00 00 00 00 : 795 + 334
    01 00 00 00 69 04 91 00 00 00 00 00 : 1129 + 145
    CD CD CD CD
    '''

    # Get the ranges for the pieces of the models
    model_ranges = []
    for x in range(pieces):
        hfile.read(4)
        model_ranges.append((int.from_bytes(hfile.read(2), byteorder='little'),
                            int.from_bytes(hfile.read(2), byteorder='little')))
        hfile.read(4)


    # Skip CDs
    if hfile.tell() % 16 != 0:
        hfile.read(16 - (hfile.tell() % 16))

    # Get shorts of the faces
    shorts = []
    for x in range(model_ranges[-1][0] + model_ranges[-1][1]):
        shorts.append(int.from_bytes(hfile.read(2), byteorder='little') + 1)

    # Get the faces
    for piece in model_ranges:
        forward = True
        for x in range(piece[0] + 2, piece[0] + piece[1]):

            if forward:
                faces.append((shorts[x - 2], shorts[x - 1], shorts[x - 0]))
                forward = False
            else:
                faces.append((shorts[x], shorts[x - 1], shorts[x - 2]))
                forward = True


    if os.path.exists("./vehicle_objs") == False:
        os.mkdir("./vehicle_objs")

    # Make obj file
    if os.path.exists("./vehicle_objs/" + fname + '.obj'):
        os.remove("./vehicle_objs/" + fname + '.obj')

    obj = open("./vehicle_objs/" + fname + '.obj', 'a')

    for vert in vertices:
        obj.write('v ' + str(vert[0]) + ' ' + str(vert[1]) + ' ' + str(vert[2]) + '\n')

    obj.write('\n')

    for uv in UVs:
        obj.write('vt ' + str(uv[0]) + ' ' + str(uv[1]) + '\n')

    obj.write('\n')

    for f in faces:
        obj.write('f ' + str(f[0]) + ' ' + str(f[1]) + ' ' + str(f[2]) + '\n')

    obj.close()


def convert_meshxbck(fname):

    hfile = open(fname, "rb")
    hfile.read(16 * 8)
    convert(hfile, fname)
    hfile.close()


def convert_gmesh(fname):

    vrootHEX = b'\x76\x72\x6F\x6F\x74'
    meshHEX = b'\x6D\x65\x73\x68\x00'

    # first find where the models are placed
    hfile = open(fname, 'rb')

    last = 0
    while 1:

        #  Find the model name start
        hfile.seek(0)
        name_start = hfile.read().find(vrootHEX, last)
        if name_start == -1:
            break

        #  Find the end of the model name
        hfile.seek(0)
        name_end = hfile.read().find(meshHEX, name_start, name_start + 200)
        if name_end == -1:
            break

        #  Get the name of the model
        hfile.seek(name_start)
        name = hfile.read(name_end + 4 - name_start).decode('ascii')
        hfile.read(1)

        #  Get the index of the start of the model
        if hfile.tell() % 16 != 0:
            hfile.read(16 - (hfile.tell() % 16))

        convert(hfile, name.strip())

        last = name_end

    hfile.close()



fnames = os.listdir()
for fname in fnames:
    if fname.endswith("mesh.xbck"):
        convert_meshxbck(fname)
    elif fname.endswith("g.xbck"):
        convert_gmesh(fname)

