provider qm {
    probe kernel_dispatch(int);

    // Dynamic Hash FS Probes
    probe dh_open_file_start(int, int, int);    // path, mode, rights
    probe dh_open_file_end(int, int);           // path, fd
    probe dh_close_file_start(int);             // fd
    probe dh_close_file_end(int);               // fd
};
