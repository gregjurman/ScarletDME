# CFLAGS
SET(CMAKE_C_FLAGS "-DLINUX -D_FILE_OFFSET_BITS=64 -DGPL -g -fPIC")

# Base library and configs
add_library(inipath inipath.c)
foreach(BaseSourcesIter analyse b64 clopts config ctype ingroup
        kernel k_error k_funcs messages netfiles object objprog
        pdump qmlib qmsem qmtermlb reccache strings sysdump sysseg
        telnet time to_file txn)
    set(BaseSources ${BaseSources} ${BaseSourcesIter}.c)
endforeach(BaseSourcesIter)
add_library(qmbase ${BaseSources})

# Linux specific
foreach(LinuxSourcesIter linuxio linuxlb linuxprt lnx lnxport)
    set(LNXSources ${LNXSources} ${LinuxSourcesIter}.c)
endforeach(LinuxSourcesIter)
add_library(qmlinux ${LNXSources})

# Distributed Hash Library
file (GLOB DHSources dh_*.c)
add_library(qmdh ${DHSources})
target_link_libraries(qmdh qmbase)

# Kernel OpCodes
file (GLOB KernelOpSources op_*.c)
add_library(qmkernelop ${KernelOpSources})
target_link_libraries(qmkernelop qmdh)

# QM daemon
add_executable(qm qm.c)
target_link_libraries(qm
    m crypt dl
    inipath
    qmbase qmdh qmkernelop qmlinux
    )

# QMCLILIB
add_library(qmclilib SHARED qmclilib.c)


# QMTic
add_executable(qmtic qmtic.c)
target_link_libraries(qmtic inipath)


# QMFix
add_executable(qmfix qmfix.c linuxlb.c ctype.c dh_hash.c)
target_link_libraries(qmfix inipath)
