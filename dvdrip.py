#!/usr/bin/python

# Copyright (c) 2012, Stephen Warren
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 
# Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# Neither the name Stephen Warren nor the names of this software's
# contributors may be used to endorse or promote products derived from this
# software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import array
import fcntl
import libdvdcss2
import os
import os.path
import re
import struct
import subprocess
import sys

dev = '/dev/cdrom'
mnt = '/mnt/tmp'

ret = os.system('mount -o ro %s %s' % (dev, mnt))
if ret != 0:
    raise Exception('Mount failed')
lba_to_file = []
for result in os.walk(mnt):
    (d, dirs, files) = result
    for f in files:
        fd = os.open(os.path.join(d, f), os.O_RDONLY)
        buf = array.array('I', [0])
        fcntl.ioctl(fd, 1, buf, True)
        is_enc = f.lower().endswith('vob')
        lba_to_file.append((buf[0], is_enc))
        os.close(fd)
lba_to_file.sort(lambda a, b: cmp(a[0], b[0]))
ret = os.system('umount %s' % mnt)
if ret != 0:
    raise Exception('Unmount failed')

h = libdvdcss2.open('/dev/cdrom')
is_scrambled = libdvdcss2.is_scrambled(h)
if not is_scrambled:
    lba_to_file = []

libdvdcss2.seek(h, 16, libdvdcss2.NOFLAGS)
buf = libdvdcss2.read(h, 1, 1)
volume_identifier = buf[40:72].strip()
volume_space_size = struct.unpack_from('<I', buf, 80)[0]

name = re.sub('[^A-Za-z0-9()_+-]', '.', volume_identifier).lower()
fn = name + '.iso'
tmpfn = name + '.tmp'

print 'Ripping %d sectors to %s' % (volume_space_size, fn)

size = volume_space_size * libdvdcss2.BLOCK_SIZE
pvcmd = "pv -p -e -r -s %d > %s" % (size, tmpfn)
fo = subprocess.Popen(pvcmd, shell=True, stdin=subprocess.PIPE).stdin

libdvdcss2.seek(h, 0, 0)
sector = 0
while sector < volume_space_size:
    if len(lba_to_file) and (sector == lba_to_file[0][0]):
        if lba_to_file[0][1]:
            flags = libdvdcss2.SEEK_MPEG | libdvdcss2.SEEK_KEY
        else:
            flags = 0
        libdvdcss2.seek(h, sector, flags)
        lba_to_file.pop(0)
    nextblock = (sector + 16) & ~15
    if len(lba_to_file) and (nextblock >= lba_to_file[0][0]):
        sectors = lba_to_file[0][0] - sector
    else:
        sectors = nextblock - sector
    buf = libdvdcss2.read(h, sectors, libdvdcss2.READ_DECRYPT)
    fo.write(buf)
    sector += sectors
sys.exit(0)

fo.close()
libdvdcss2.close(h)

os.rename(tmpfn, fn)
