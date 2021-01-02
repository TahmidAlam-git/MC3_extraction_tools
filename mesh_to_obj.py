#!/usr/bin/python3
import os
import math
import struct
import easygui

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


def convert_meshxbck(path):

    hfile = open(path, "rb")
    hfile.read(16 * 8)
    convert(hfile, path.split("\\")[-1])
    hfile.close()


def convert_gmesh(path):

    vrootHEX = b'\x76\x72\x6F\x6F\x74'
    meshHEX = b'\x6D\x65\x73\x68\x00'

    # first find where the models are placed
    hfile = open(path, 'rb')
    fname = path.split("\\")[-1]

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


def align_16(hfile):
    if hfile.tell() % 16 != 0:
        hfile.read(16 - (hfile.tell() % 16))


def find_models(hfile, name_starts_with_b):
    print("looking for files")
    name_ending_with_b = bytes(1)
    name_and_offsets = []  # type = Tuple, (name, offset to the header)

    last = 0
    while 1:

        #  Find the model name start
        hfile.seek(0)
        name_start = hfile.read().find(name_starts_with_b, last)
        if name_start == -1:
            break

        #  Find the end of the model name
        hfile.seek(name_start)
        name_len = hfile.read().find(name_ending_with_b)
        if name_len == -1:
            break

        #  Get the name of the model
        hfile.seek(name_start + 1)
        name = hfile.read(name_len - 1).decode('utf-8')
        hfile.read(1)

        align_16(hfile)
        name_and_offsets.append((name, hfile.tell()))
        last = name_start + name_len
        #print("found: " + name)

    return name_and_offsets


def read_model_header(hfile):
    hfile.read(7)
    padding = int.from_bytes(hfile.read(1), byteorder='little') - 12
    face_sections = int.from_bytes(hfile.read(2), byteorder='little')
    ff_sections = int.from_bytes(hfile.read(2), byteorder='little')
    hfile.read(4)

    # unknown line
    hfile.read(16)

    # face thing
    hfile.read(face_sections * 2)
    align_16(hfile)

    # set thing
    set_sections = int.from_bytes(hfile.read(2), byteorder='little')
    hfile.read(2)
    hfile.read(set_sections * 24)

    # ending of header thing
    hfile.read(12)
    align_16(hfile)

    return padding, face_sections, ff_sections


def read_face_header(hfile, face_sections, ff_exists):
    face_ranges = []
    for x in range(face_sections):
        hfile.read(4)
        face_ranges.append((int.from_bytes(hfile.read(2), byteorder='little'),
                            int.from_bytes(hfile.read(2), byteorder='little')))
        hfile.read(4)

    #if ff_exists:
    #    hfile.read(4)
    #align_16(hfile)

    while hfile.read(1) == b'\xCD':
        pass

    hfile.seek(-1, 1)

    return face_ranges


def read_ff_header(hfile, ff_sections):
    hfile.read(4)
    hfile.read(ff_sections * 4)

def read_ff(hfile, ff_num):
    hfile.read(12)
    align_16(hfile)

    hfile.read(4 * ff_num)


def read_vertices_uv(hfile, padding):

    vertices = []
    uvs = []
    uv_padding = padding - 8

    # TODO: find the amount of vertices from header instead
    # get the vertices and UVs
    while 1:
        x = struct.unpack('f', hfile.read(4))[0]
        y = struct.unpack('f', hfile.read(4))[0]
        z = struct.unpack('f', hfile.read(4))[0]

        # check if we are at the faces header
        hfile.seek(-12, 1)
        a = hfile.read(1)
        b = hfile.read(1)
        c = hfile.read(1)
        d = hfile.read(1)
        hfile.read(4)
        e = hfile.read(1)
        f = hfile.read(1)
        g = hfile.read(1)
        h = hfile.read(1)

        # only way to find when the vertices end
        if a == b'\x01' and b == c == d == e == f == g == h == b'\x00':
            hfile.seek(-12, 1)
            break

        vertices.append((x, y, z))

        hfile.read(uv_padding)
        uva = struct.unpack('f', hfile.read(4))[0]
        uvb = struct.unpack('f', hfile.read(4))[0]
        uvs.append((uva, uvb))

    return vertices, uvs


def read_faces(hfile, model_ranges):
    faces = []

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

    align_16(hfile)

    return faces


def write_model(folder, name, vertices, uvs, faces):

    # make folder
    if os.path.exists("./" + folder) == False:
        os.mkdir("./" + folder)

    # Make obj file
    if os.path.exists("./" + folder + "/" + name + ".obj"):
        os.remove("./" + folder + "/" + name + ".obj")

    obj = open("./" + folder + "/" + name + ".obj", 'a')

    for vert in vertices:
        obj.write('v ' + str(vert[0]) + ' ' + str(vert[1]) + ' ' + str(vert[2]) + '\n')

    for uv in uvs:
        obj.write('vt ' + str(uv[0]) + ' ' + str(uv[1]) + '\n')

    for f in faces:
        obj.write('f ' + str(f[0]) + ' ' + str(f[1]) + ' ' + str(f[2]) + '\n')

    obj.close()



def read_map(file_name, lookfor):
    hfile = open(file_name, 'rb')
    model_offsets = find_models(hfile, lookfor)

    check = {}

    print("found %d model files" % len(model_offsets))

    if os.path.exists("./" + "structures") == False:
        os.mkdir("./" + "structures")

    for z, model in enumerate(model_offsets):
        name = model[0]
        offset = model[1]

        hfile.seek(offset)

        for y in range(50):

            #print("starting of model", hex(hfile.tell()))

            padding, face_sections, ff_sections = read_model_header(hfile)

            #print("padding:", padding, "face_sections:", face_sections, "ff_sections:", ff_sections)

            #print("starting of vertices", hex(hfile.tell()))

            # currently the only way to know when to stop looking for pieces of 1 model
            if not (padding == 8 or padding == 12 or padding == 16 or padding == 20):
                break

            vertices, uvs = read_vertices_uv(hfile, padding)

            #print("starting of face header", hex(hfile.tell()))

            face_range = read_face_header(hfile, face_sections, ff_sections > 0)

            #print("starting of ff header", hex(hfile.tell()))

            if ff_sections > 0:
                read_ff_header(hfile, ff_sections)

            #print("starting of ff", hex(hfile.tell()))

            for x in range(ff_sections):
                read_ff(hfile, len(vertices))

            align_16(hfile)  # fix this

            #print("starting of faces", hex(hfile.tell()))

            faces = read_faces(hfile, face_range)

            check[name] = z
            write_model("structures/" + name, name + "_part" + str(y + 1), vertices, uvs, faces)
            print("Success!: " + name + "_part" + str(y + 1) + " #" + str(z + 1))

    for m in model_offsets:
        if m[0] not in check:
            print("Unsuccessful: " + m[0])


print("Starting file explorer, please wait")
path = easygui.fileopenbox()

# TODO: add more subfolders for vehicles and map models for better searchability
# TODO: change mesh.xbck and g.xbck to the new way that read_map is now for readability and code style
if path.endswith("mesh.xbck"):
    convert_meshxbck(path)

elif path.endswith("g.xbck"):
    convert_gmesh(path)

elif path.split("\\")[-1].startswith("sd"):
    read_map(path, b'\xCD\x73\x5F')

#elif path.split("\\")[-1].startswith("atlanta"):
#    read_map(path, b'xCD\x61\x5F')

#elif path.split("\\")[-1].startswith("detroit"):
#    read_map(path, b'xCD\x64\x5F')



