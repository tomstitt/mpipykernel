import os
import shutil
import sys
import glob
from distutils.core import setup
from distutils.spawn import find_executable

from ipykernel.kernelspec import write_kernel_spec, make_ipkernel_cmd

distname = "mpipykernel"

if "NPROCS" in os.environ:
    nprocs = int(os.environ["NPROCS"])
    if nprocs < 1:
        sys.exit("NPROCS must be >= 1")
else:
    nprocs = 2

if "MPIRUN" in os.environ:
    mpirun = os.environ["MPIRUN"]
else:
    mpirun = "mpirun"
    
mpirun = find_executable(mpirun)
if mpirun is None:
    sys.exit("unable to find mpirun exe '%s'" % mpirun)

setup_args = dict(
    name=distname,
    packages=[distname],
    # =p
    install_require=["ipykernel", "mpi4py"]
)

# create kernelspec
here = os.path.abspath(os.path.dirname(__file__))
dest = os.path.join(here, "data_kernelspec")
if os.path.exists(dest):
    shutil.rmtree(dest)

version = sys.version_info[0]
argv = [mpirun, "-n", str(nprocs), sys.executable, "-m", "%s.%s" % (distname, distname), "-f", "{connection_file}"]
write_kernel_spec(dest, overrides={"argv": argv, "display_name": "MPI Python %d (np=%d)" % (version, nprocs)})
kernel_name = "mpipython%d_np%d" % (version, nprocs)
setup_args["data_files"] = [(("share/jupyter/kernels/%s" % kernel_name), glob.glob("data_kernelspec/*"))]

setup(**setup_args)
