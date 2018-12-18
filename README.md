# MPI IPython Kernel for Jupyter

A basic mpi+ipython kernel using mpi4py. Exports `rank`, `comm`, `nprocs`, and `mpiprint` into the global
namespace.

```python
>>> nprocs
4

>>> mpiprint("hello from %d" % rank)
hello from 0
hello from 1
hello from 2
hello from 3

>>> comm
<mpi4py.MPI.Intracomm at 0x10ba38468>
```

## Installation

To install with the defaults (mpiexec=mpirun, npocs=2)

```shell
pip install .
```

To change:

```shell
[MPIRUN=] [NPROCS=] pip install .
```

## Usage

You can select the kernel from the "New" menu but you're stuck with a fixed number of processors for now.

You may also launch the kernel yourself and connect:

```shell
mpirun -n 4 python -m mpipykernel.mpipykernel
```

or embed the kernel:

```
mpirun -n 4 python -c "s = 'hi from %d'; from mpipykernel import embed; embed(locals())"

...

>>> mpiprint(s%rank)
hi from 0
hi from 1
hi from 2
hi from 3
```
