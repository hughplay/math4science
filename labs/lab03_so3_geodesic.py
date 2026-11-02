"""Compare SO(3) geodesic interpolation to linear matrix interpolation. pip install numpy scipy"""
import numpy as np
from scipy.spatial.transform import Rotation
a=Rotation.from_euler("z",90,degrees=True).as_matrix()
eye=np.eye(3)
relative=Rotation.from_matrix(eye.T@a)
for t in np.linspace(0,1,6):
    linear=(1-t)*eye+t*a
    geodesic=eye@Rotation.from_rotvec(t*relative.as_rotvec()).as_matrix()
    def orth_err(m): return np.linalg.norm(m.T@m-np.eye(3))
    print(f"t={t:.1f} linear_err={orth_err(linear):.5f} geodesic_err={orth_err(geodesic):.5e} det_linear={np.linalg.det(linear):.3f}")
