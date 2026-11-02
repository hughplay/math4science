"""2-D conditional flow matching toy experiment. pip install torch matplotlib"""
import torch
from torch import nn
import matplotlib.pyplot as plt
torch.manual_seed(42)
device = "cuda" if torch.cuda.is_available() else "cpu"
net = nn.Sequential(nn.Linear(3,128),nn.SiLU(),nn.Linear(128,128),nn.SiLU(),nn.Linear(128,2)).to(device)
opt = torch.optim.Adam(net.parameters(),lr=1e-3)
def target(n):
    theta = torch.rand(n,device=device)*2*torch.pi
    return torch.stack([2*theta.cos(),2*theta.sin()],dim=1)+0.15*torch.randn(n,2,device=device)
for step in range(2000):
    x0=torch.randn(512,2,device=device); x1=target(512)
    t=torch.rand(512,1,device=device); xt=(1-t)*x0+t*x1
    pred=net(torch.cat([xt,t],dim=1))
    loss=((pred-(x1-x0))**2).mean()
    opt.zero_grad(); loss.backward(); opt.step()
    if step%500==0: print(step,round(loss.item(),4))
with torch.no_grad():
    x=torch.randn(2000,2,device=device)
    dt=1/100
    for i in range(100):
        t=torch.full((len(x),1),i*dt,device=device)
        x=x+dt*net(torch.cat([x,t],dim=1))
    x=x.cpu()
plt.scatter(x[:,0],x[:,1],s=2,alpha=.5)
plt.axis("equal");plt.title("2D flow matching samples");plt.show()
