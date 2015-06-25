provider qm {
    probe kernel_dispatch(int);

    // Dynamic Hash FS Probes
    probe dh_open_file_start(int, int, int);    // path, mode, rights
    probe dh_open_file_end(int, int);           // path, fd
    probe dh_close_file_start(int);             // fd
    probe dh_close_file_end(int);               // fd

    // Record locks (local)
    probe lock_record_local_start(int);         // txn_id
    probe lock_record_local_end(int);           // txn_id
    probe lock_record_local_abort(int, int);    // txn_id, status
    probe unlock_record_local_start();          //
    probe unlock_record_local_end(int);         // status
};
