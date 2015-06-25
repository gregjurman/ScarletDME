import struct
import mmap
import shutil

class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


class HeaderFlags(object):
    CPROC=0x0001
    INTERNAL=0x0002
    DEBUG=0x0004
    DEBUGGER=0x0008
    NOCASESTRING=0x0010
    FUNC=0x0020
    VARARGS=0x0040
    RECURSIVE=0x0080
    ITYPE=0x0100
    ALLOWBRK=0x0200
    TRUSTED=0x0400
    NETFILES=0x0800
    CASESENSITIVE=0x1000
    QMCALL=0x2000
    CTYPE=0x4000
    CLASS=0x8000

    _header_flags = {
        0x0001:"CPROC",
        0x0002:"INTERNAL",
        0x0004:"DEBUGMODE",
        0x0008:"DEBUGGER",
        0x0010:"NOCASESTRING",
        0x0020:"FUNC",
        0x0040:"VARARGS",
        0x0080:"RECURSIVE",
        0x0100:"ITYPE",
        0x0200:"ALLOWBRK",
        0x0400:"TRUSTED",
        0x0800:"NETFILES",
        0x1000:"CASESENSITIVE",
        0x2000:"QMCALL",
        0x4000:"CTYPE",
        0x8000:"CLASS"
        }


class CodeSegment:
    SYMTAB = 1
    LINETAB = 2
    CODE = 4


class CodeObject(object):
    def __init__(self, path):
        self.path = path
        self.fi = open(path, "r+b")

    def _header_flags(self, raw_flags=0):
        return [HeaderFlags._header_flags[k] for k in iter(HeaderFlags._header_flags) if (raw_flags & k==k)]

    def _get_header(self):
        self.fi.seek(0)
        obj = mmap.mmap(self.fi.fileno(), 0)
        magic = struct.unpack("b", obj[0])[0]
        endian = {100:"LITTLE", 101: "BIG"}.get(magic, "UNKNOWN")
        rev = struct.unpack("b", obj[1])[0]
        _id = struct.unpack("I", obj[2:6])[0]
        start = struct.unpack("I", obj[6:10])[0]
        arg_count = struct.unpack("H", obj[10:12])[0]
        var_count = struct.unpack("H", obj[12:14])[0]
        max_stack = struct.unpack("H", obj[14:16])[0]
        sym_tab_offset = struct.unpack("I", obj[16:20])[0]
        line_tab_offset = struct.unpack("I", obj[20:24])[0]
        obj_size = struct.unpack("I", obj[24:28])[0]
        flags_raw = struct.unpack("H", obj[28:30])[0]
        flags = self._header_flags(flags_raw)
        compile_time = struct.unpack("I", obj[30:34])[0]
        refs = struct.unpack("H", obj[34:36])[0]
        name = str(obj[36:165]).rstrip("\0")

        _header = AttributeDict(
            magic=magic,
            endian=endian,
            rev=rev,
            id=_id,
            start=start,
            arg_count=arg_count,
            var_count=var_count,
            max_stack=max_stack,
            sym_tab_offset=sym_tab_offset,
            line_tab_offset=line_tab_offset,
            obj_size=obj_size,
            flags=flags,
            compile_time=compile_time,
            refs=refs,
            name=name,
        )
        obj.close()

        return _header

    def _get_segment(self, segment):
        seg = None
        obj = mmap.mmap(self.fi.fileno(), 0)
        _start = 0
        _end = 0
        if segment == CodeSegment.SYMTAB:
            _start = self._get_header().sym_tab_offset
            _end = self._get_header().obj_size
            if _start is 0:
                return None # No Symbol Table
        elif segment == CodeSegment.LINETAB:
            _start = self._get_header().line_tab_offset
            _end = self._get_header().sym_tab_offset
            if _start is 0:
                return None # No Line Table
        elif segment == CodeSegment.CODE:
            _start = self._get_header().start
            _end = self._get_header().line_tab_offset
            if _end is 0:
                _end = self._get_header().obj_size
        else:
            return None # Nothing here

        seg = obj[_start:_end]
        obj.close()

        return seg

    def make_no_xref(self, new_path=None):
        if new_path is None:
            new_path = "%s.noxref" % self.path

        shutil.copy(self.path, new_path)
        new_fi = open(new_path, "r+b")
        new_obj = mmap.mmap(new_fi.fileno(), 0)
        obj = mmap.mmap(self.fi.fileno(), 0)
        obj_size = self._get_header().obj_size
        sym_tab_off = self._get_header().sym_tab_offset
        if sym_tab_off: obj_size = sym_tab_off
        line_tab_off = self._get_header().line_tab_offset
        if line_tab_off: obj_size = line_tab_off
        new_obj[24:28] = struct.pack("I", obj_size)
        new_obj[16:20] = struct.pack("I", 0)
        new_obj[20:24] = struct.pack("I", 0)
        new_obj.resize(obj_size)
        new_obj.flush()

        new_obj.close()
        obj.close()

if __name__ == "__main__":
    comp = CodeObject("test.comp")
    print comp._get_header()
    comp.make_no_xref()
