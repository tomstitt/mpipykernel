#
# basic mpi+ipykernel kernel
# exports rank, comm, nprocs, and mpiprint
# use like: mpirun -n 4 python mpipykernel.py [-c {conn_file}]
#

from __future__ import print_function
import sys
from ipykernel.ipkernel import IPythonKernel

from mpi4py import MPI
comm = MPI.COMM_WORLD
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


mpi_ns = dict(rank=rank, comm=comm, nprocs=nprocs, mpiprint=mpiprint)


class MPIPythonKernel(IPythonKernel):
    def do_execute(self, code, silent, *args, **kws):
        comm.bcast(code, root=0)
        return super().do_execute(code, silent, *args, **kws)


def non_root_execute_loop():
    while True:
        #debug("%d: waiting for input" % rank)
        code = None
        code = comm.bcast(code, root=0)
        #debug("%d: got code: %s" % (rank, code))
        # TODO: handle better
        if code == "quit":
            break
        try:
            exec(code)
        except:
            # TODO: log
            pass


if __name__ == "__main__":
    from ipykernel.kernelapp import IPKernelApp
    if rank == 0:
        IPKernelApp.launch_instance(kernel_class=MPIPythonKernel, user_ns=mpi_ns)
    else:
        non_root_execute_loop()
