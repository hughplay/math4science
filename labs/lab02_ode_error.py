"""Compare Euler and midpoint convergence on dx/dt = -x. pip install numpy matplotlib"""
import numpy as np
import matplotlib.pyplot as plt
steps=np.array([5,10,20,40,80,160])
euler=[];midpoint=[]
for n in steps:
    dt=1/n
    x=y=1.
    for _ in range(n):
        x+=dt*(-x)
        k1=-y
        k2=-(y+dt*k1/2)
        y+=dt*k2
    euler.append(abs(x-np.exp(-1)))
    midpoint.append(abs(y-np.exp(-1)))
plt.loglog(steps,euler,"o-",label="Euler (order 1)")
plt.loglog(steps,midpoint,"o-",label="Midpoint (order 2)")
plt.xlabel("Number of steps");plt.ylabel("Absolute error at t=1")
plt.legend();plt.grid(True);plt.show()
