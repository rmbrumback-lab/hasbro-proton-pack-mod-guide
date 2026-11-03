import numpy as np
def fit_circle(p):
    p=np.asarray(p,float); x,y=p[:,0],p[:,1]
    A=np.c_[2*x,2*y,np.ones(len(x))]; b=x*x+y*y
    c,*_=np.linalg.lstsq(A,b,rcond=None); cx,cy=c[0],c[1]; r=np.sqrt(c[2]+cx*cx+cy*cy)
    res=np.hypot(x-cx,y-cy)-r
    return cx,cy,r,res
def robust_circle(p,k=2.5,it=4):
    p=np.asarray(p,float); m=np.ones(len(p),bool)
    for _ in range(it):
        cx,cy,r,res=fit_circle(p[m]); allres=np.hypot(p[:,0]-cx,p[:,1]-cy)-r
        s=1.4826*np.median(np.abs(allres[m])); m=np.abs(allres)<max(k*s,0.05)
    cx,cy,r,res=fit_circle(p[m]); return cx,cy,r,res,m
