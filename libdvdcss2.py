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

from ctypes import *

_dll = cdll.LoadLibrary('libdvdcss.so.2')

# Public API: Constants

BLOCK_SIZE = 2048
NOFLAGS = 0
READ_DECRYPT = 1
SEEK_MPEG = 1
SEEK_KEY = 2

# Public API: Exception types

class LibDvdCss2Exception(Exception):
    def __init__(self, func, result):
        self.func = func
        self.result = result

    def __str__(self):
        return 'libdvdcss2 function %s failed with error value %s' % (
            repr(self.func),
            repr(self.result)
        )

# Internal helpers for error checking

def _errcheck_non_zero(func_name):
    def _checker(*args):
        result = args[0]
        if result == 0:
            raise LibDvdCss2Exception(func_name, result)
        return result
    return _checker

def _errcheck_non_negative(func_name):
    def _checker(*args):
        result = args[0]
        if result < 0:
            raise LibDvdCss2Exception(func_name, result)
        return result
    return _checker

# Public API: Function prototypes

# dvdcss_t dvdcss_open(char *psz_target);
open = CFUNCTYPE(
    c_long,
    c_char_p
)(('dvdcss_open', _dll))
open.errcheck = _errcheck_non_zero('dvdcss_open')

# int dvdcss_close(dvdcss_t);
close = CFUNCTYPE(
    c_int,
    c_long
)(('dvdcss_close', _dll))
close.errcheck = _errcheck_non_negative('dvdcss_close')

# int dvdcss_seek(dvdcss_t, int i_blocks, int i_flags);
seek = CFUNCTYPE(
    c_int,
    c_long,
    c_int,
    c_int
)(('dvdcss_seek', _dll))
seek.errcheck = _errcheck_non_negative('dvdcss_seek')

# int dvdcss_read(dvdcss_t, void *p_buffer, int i_blocks, int i_flags);
_read = CFUNCTYPE(
    c_int,
    c_long,
    c_char_p,
    c_int,
    c_int
)(('dvdcss_read', _dll))
_read_buf = None
_read_buf_blocks = 0
def read(dvdcss_t, blocks, flags):
    global _read_buf
    global _read_buf_blocks
    if _read_buf_blocks < blocks:
        _read_buf = create_string_buffer(blocks * BLOCK_SIZE)
        _read_buf_blocks = blocks
    ret = _read(dvdcss_t, _read_buf, blocks, flags)
    if ret != blocks:
        raise LibDvdCss2Exception('dvdcss_read', 'ret != %d' % blocks)
    return _read_buf

# char *dvdcss_error(dvdcss_t);
error = CFUNCTYPE(
    c_int,
    c_long
)(('dvdcss_error', _dll))

# int dvdcss_is_scrambled(dvdcss_t);
is_scrambled = CFUNCTYPE(
    c_int,
    c_long
)(('dvdcss_is_scrambled', _dll))
