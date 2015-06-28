import code


if __name__ == "__main__":
    comp = code.CodeObject.create_from_file("BCOMP")
    print comp._header
    print
    noxref = comp.make_noxref()

    pobj = code.CodeCatalog.create_from_file("pcode")

    newpobj = code.CodeCatalog.create_from_iter(pobj.catalog.values())

    newpobj.catalog['OCONV'].write("OCONV.out")
    newpobj.write("newpcode2")
