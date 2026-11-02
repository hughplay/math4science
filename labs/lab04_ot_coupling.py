"""Toy optimal vs random coupling. pip install numpy scipy matplotlib"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linear_sum_assignment
rng=np.random.default_rng(7)
n=35
x0=rng.normal([-2,0],[.55,.55],(n,2))
x1=rng.normal([2,0],[.55,.55],(n,2))
cost=((x0[:,None,:]-x1[None,:,:])**2).sum(-1)
_,j=linear_sum_assignment(cost)
random_j=rng.permutation(n)
fig,axes=plt.subplots(1,2,figsize=(10,4))
for ax,order,title in zip(axes,[random_j,j],["Random coupling","OT (assignment) coupling"]):
    for a,b in zip(x0,x1[order]):
        ax.plot([a[0],b[0]],[a[1],b[1]],alpha=.4)
    ax.scatter(*x0.T,s=15);ax.scatter(*x1.T,s=15)
    ax.set_title(f"{title}, cost={cost[np.arange(n),order].mean():.2f}")
    ax.axis("equal")
plt.tight_layout();plt.show()
