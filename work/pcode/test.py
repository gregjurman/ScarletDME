import struct
import mmap
import shutil
import os
import cStringIO as csio
from collections import namedtuple as _nt


CodeHeaderBase = _nt("CodeHeader", (
    "magic", "endian", "revision", "id", "start", "arg_count",
    "var_count", "max_stack", "symbol_table_offset",
    "line_table_offset", "object_size", "flags", "compile_time",
    "refs", "name"))


class HeaderFlags(object):
    _flags = (
        (0x0001, 0x0002,0x0004, 0x0008,
        0x0010, 0x0020, 0x0040, 0x0080,
        0x0100, 0x0200, 0x0400, 0x0800,
        0x1000, 0x2000, 0x4000, 0x8000),
        ("CPROC", "INTERNAL", "DEBUGMODE", "DEBUGGER",
        "NOCASESTRING", "FUNC", "VARARGS", "RECURSIVE",
        "ITYPE", "ALLOWBRK", "TRUSTED", "NETFILES",
        "CASESENSITIVE", "QMCALL", "CTYPE", "CLASS")
    )

    def __init__(self, flags):
        self.flags = flags

    def __str__(self):
        return ", ".join([self._flags[1][i] for i, k in zip(range(16), self._flags[0]) if (self.flags & k==k)])

    def __repr__(self):
        return "<HeaderFlags: %s>" % self

    def __getattr__(self, attrname):
        a = self._flags[0][self._flags[1].index(attrname.upper())]
        return self.flags & a == a

    def __int__(self):
        return self.flags


class CodeHeader(CodeHeaderBase):
    def __init__(self, **kwargs):
        super(CodeHeader, self).__init__(**kwargs)

    @classmethod
    def unpack(self, data):
        obj = memoryview(data)
        h_raw = list(struct.unpack("=bbIIHHHIIIHIH129s", obj[0:165]))
        h_raw.insert(1, {100: "LITTLE", 101: "BIG"}.get(h_raw[0], "UNKNOWN"))
        h_raw[-1] = h_raw[-1].rstrip("\0")
        h_raw[-4] = HeaderFlags(h_raw[-4])

        return CodeHeader(**dict(zip(CodeHeader._fields, h_raw)))

    def replace(self, **kwargs):
        return self._replace(**kwargs)

    def pack(self):
        arr = list(self)
        del arr[1]
        print arr
        return struct.pack("=bbIIHHHIIIHIH129s", *arr)

class CodeSegment:
    SYMTAB = 1
    LINETAB = 2
    CODE = 4


class CodeObject(object):
    def __init__(self, data, path=None):
        self.path = path
        self._data = data
        self._header = self._get_header()

    def __repr__(self):
        return "<CodeObject '%s': size=%i, flags=[%s]>" % (
                self._header.name, self._header.object_size,
                self._header.flags)

    @classmethod
    def create_from_file(self, path):
        out = None
        with open(path, "r+b") as fobj:
            out = CodeObject(fobj.read(), path)
        return out

    def change_header(self, **kwargs):
        self._header = self._header.replace(**kwargs)

    def _get_header(self):
        obj = memoryview(self._data)
        _header = CodeHeader.unpack(obj[0:165])

        return _header

    def _get_segment(self, segment):
        _header = self._header
        obj = memoryview(self._data)
        _start = 0
        _end = 0
        if segment == CodeSegment.SYMTAB:
            _start = _header.symbol_table_offset
            _end = _header.object_size
            if _start is 0:
                return None # No Symbol Table
        elif segment == CodeSegment.LINETAB:
            _start = _header.line_table_offset
            _end = _header.symbol_table_offset
            if _start is 0:
                return None # No Line Table
        elif segment == CodeSegment.CODE:
            _start = _header.start
            _end = _header.line_table_offset
            if _end is 0:
                _end = _header().object_size
        else:
            return None # Nothing here

        seg = obj[_start:_end]
        obj.close()

        return seg

    def clone(self):
        return CodeObject(""+self._data, self.path)

    def truncate(self, new_size):
        if new_size > len(self._data):
            raise ValueError("New size must be less than current size")
        self._data = self._data[0:new_size+1]

    def make_noxref(self):
        new_obj = self.clone()
        _header = self._get_header()
        obj_size = _header.object_size
        sym_tab_off = _header.symbol_table_offset
        if sym_tab_off: obj_size = sym_tab_off
        line_tab_off = _header.line_table_offset
        if line_tab_off: obj_size = line_tab_off
        new_obj.change_header(symbol_table_offset=0, line_table_offset=0, object_size=obj_size)
        new_obj.truncate(obj_size)

        return new_obj

    def is_recursive(self):
        _header = self._get_header()
        return os.path.basename(self.path)[0] == "_" and _header.flags.recursive


class PCodeCatalog(object):
    def __init__(self, data, path=None):
        self.path = path
        self._data = data
        self._generate_cache()

    @classmethod
    def create_from_file(self, path):
        out = None
        with open(path, "r+b") as fobj:
            out = PCodeCatalog(fobj.read(), path)
        return out

    def _generate_cache(self):
        obj = memoryview(self._data)
        self.catalog = {}
        i = 0
        while i < len(obj):
            pname = obj[i+36:i+999].tobytes().split("\0", 1)[0]
            j = (struct.unpack("I", obj[i+24:i+28])[0]+3) & (~0x03)

            self.catalog[pname] = CodeObject(obj[i:i+j+1])
            i += j


if __name__ == "__main__":
    comp = CodeObject.create_from_file("BCOMP")
    print comp._header
    print
    noxref = comp.make_noxref()

    pobj = PCodeCatalog.create_from_file("pcode")
    print pobj.catalog
