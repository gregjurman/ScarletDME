import struct
import mmap
import shutil
from collections import namedtuple as _nt


CodeHeader = _nt("CodeHeader", (
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


class CodeSegment:
    SYMTAB = 1
    LINETAB = 2
    CODE = 4


class CodeObject(object):
    def __init__(self, path):
        self.path = path
        self.fi = open(path, "r+b")

    def _get_header(self):
        self.fi.seek(0)
        obj = mmap.mmap(self.fi.fileno(), 0)
        h_raw = list(struct.unpack("=bbIIHHHIIIHIH129s", obj[0:165]))
        h_raw.insert(1, {100:"LITTLE", 101: "BIG"}.get(h_raw[0], "UNKNOWN"))
        h_raw[-1] = h_raw[-1].rstrip("\0")
        h_raw[-4] = HeaderFlags(h_raw[-4])
        obj.close()

        _header = CodeHeader(**dict(zip(CodeHeader._fields, h_raw)))
        return _header

    def _get_segment(self, segment):
        _header = self._get_header()
        obj = mmap.mmap(self.fi.fileno(), 0)
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

    def make_no_xref(self, new_path=None):
        if new_path is None:
            new_path = "%s.noxref" % self.path

        _header = self._get_header()
        shutil.copy(self.path, new_path)
        new_fi = open(new_path, "r+b")
        new_obj = mmap.mmap(new_fi.fileno(), 0)
        obj = mmap.mmap(self.fi.fileno(), 0)
        obj_size = _header.object_size
        sym_tab_off = _header.symbol_table_offset
        if sym_tab_off: obj_size = sym_tab_off
        line_tab_off = _header.line_table_offset
        if line_tab_off: obj_size = line_tab_off
        new_obj[16:28] = struct.pack("=III", 0, 0, obj_size)
        new_obj.resize(obj_size)
        new_obj.flush()

        new_obj.close()
        obj.close()

        return CodeObject(new_path)

    def is_recursive(self):
        _header = self._get_header()
        return _header.name[0] == "_" and _header.flags.recursive


if __name__ == "__main__":
    comp = CodeObject("test.comp")
    print comp._get_header()
    print

    new_file = comp.make_no_xref()
    print new_file._get_header().flags.internal
    print new_file._get_header().flags.recursive
    print new_file.is_recursive()
