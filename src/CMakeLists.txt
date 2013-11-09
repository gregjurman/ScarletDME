# CFLAGS
SET(CMAKE_C_FLAGS "-DLINUX -D_FILE_OFFSET_BITS=64 -DGPL -g -fPIC")

# Base library and configs
add_library(analyse analyse.c)
add_library(b64 b64.c)
add_library(clopts clopts.c)
add_library(config config.c)
add_library(ctype ctype.c)
add_library(inipath inipath.c)
add_library(ingroup ingroup.c)
add_library(kernel kernel.c)
add_library(k_error k_error.c)
add_library(k_funcs k_funcs.c)
add_library(messages messages.c)
add_library(netfiles netfiles.c)
add_library(object object.c)
add_library(objprog objprog.c)
add_library(pdump pdump.c)
add_library(qmlib qmlib.c)
add_library(qmsem qmsem.c)
add_library(qmtermlb qmtermlb.c)
add_library(reccache reccache.c)
add_library(strings strings.c)
add_library(sysdump sysdump.c)
add_library(sysseg sysseg.c)
add_library(telnet telnet.c)
add_library(time time.c)
add_library(to_file to_file.c)
add_library(txn txn.c)

# Linux specific
foreach(LNXV linuxio linuxlb linuxprt lnx lnxport)
    add_library(${LNXV} ${LNXV}.c)
endforeach(LNXV)

# Distributed Hash Library
file (GLOB DHSources dh_*.c)
add_library(dh ${DHSources})

# Kernel OpCodes
file (GLOB KernelOpSources op_*.c)
add_library(kernelop ${KernelOpSources})

add_executable(qm qm.c)
target_link_libraries(qm
    m crypt dl
    ${TARGET_OBJECTS}
    )
