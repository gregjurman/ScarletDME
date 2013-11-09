# CFLAGS
SET(CMAKE_C_FLAGS "-DLINUX -D_FILE_OFFSET_BITS=64 -DGPL -g -fPIC")

# Base library and configs
foreach(BaseSourcesIter analyse b64 clopts config ctype inipath ingroup
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

add_executable(qm qm.c)
target_link_libraries(qm
    m crypt dl
    qmbase qmdh qmkernelop qmlinux
    )
