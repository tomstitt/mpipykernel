#
# basic mpi+ipykernel kernel
# exports rank, comm, nprocs, and mpiprint
# use like: mpirun -n 4 python mpipykernel.py [-c {conn_file}]
# be careful with magics, they'll only execute on rank 0
#

from __future__ import print_function
import sys
import os
import signal
from ipykernel.ipkernel import IPythonKernel
from mpi4py import MPI


class MPIPythonKernel(IPythonKernel):
    def __init__(self, *args, **kwargs):
        IPythonKernel.__init__(self, *args, **kwargs)
        self.comm = self.parent.comm
        # self.shell_handlers["interrupt_request"] = self.interrupt_request

    def do_execute(self, code, silent, *args, **kwargs):
        self.comm.bcast(code, root=0)
        return IPythonKernel.do_execute(self, code, silent, *args, **kwargs)

    # TODO
    #def interrupt_request(self, stream, ident, parent):


def non_root_execute_loop(comm, local_ns):
    go = True
    def stop():
        nonlocal go
        go = False
    local_ns["quit"] = stop
    local_ns["exit"] = stop
    while go:
        code = comm.bcast(None, root=0)
        if code == "quit" or code == "exit":
            break
        try:
            exec(code, {}, local_ns)
        except Exception:
            pass


def update_ns(ns, comm):
    rank = comm.Get_rank()
    nprocs = comm.Get_size()

    def mpiprint(value, ranks=range(nprocs), *args, **kws):
        if rank == 0:
            print(value, *args, **kws)
        if len(ranks) > 0:
            for r in ranks:
                if r == 0:
                    continue
                elif r >= nprocs:
                    # TODO: warn
                    continue
                elif rank == r:
                    comm.send(value, dest=0)
                elif rank == 0:
                    val = comm.recv(source=r)
                    print(val, *args, **kws)
    ns["comm"] = comm
    ns["rank"] = rank
    ns["nprocs"] = nprocs
    ns["mpiprint"] = mpiprint
    return ns


def embed(comm, local_ns, **kwargs):
    from ipykernel.embed import embed_kernel
    update_ns(comm, local_ns)
    rank = comm.Get_rank()
    if rank == 0:
        embed_kernel(kernel_class=MPIPythonKernel, comm=comm, local_ns=local_ns, **kwargs)
    else:
        non_root_execute_loop(comm, local_ns)


if __name__ == "__main__":
    from ipykernel.kernelapp import IPKernelApp
    comm = MPI.COMM_WORLD
    ns = update_ns({}, comm)
    rank = comm.Get_rank()
    if rank == 0:
        IPKernelApp.launch_instance(kernel_class=MPIPythonKernel, comm=comm, user_ns=ns)
    else:
        non_root_execute_loop(comm, ns)
