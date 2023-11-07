import numpy as np
import time
import sys
import mueller_convolver as mc

#import litebird_sim as lbs
#import healpy as h

start = time.time()  

nthreads = int(sys.argv[1])
vnode = int(sys.argv[2])
vcore = int(sys.argv[3])
vnode_mem = int(sys.argv[4])
lmax = 383 # sky, beam lmax
kmax = 140 # beam mmax, Input lmax-4 or less.
nptg=60*60*24 # number of pointings

def nalm(lmax, mmax):
    return ((mmax+1)*(mmax+2))//2 + (mmax+1)*(lmax-mmax)

def blm_gauss_new(fwhm, lmax, pol=False):
    fwhm = float(fwhm)
    lmax = int(lmax)
    pol = bool(pol)
    mmax = 2 if pol else 0
    ncomp = 3 if pol else 1
    nval = hp.Alm.getsize(lmax, mmax)

    if mmax > lmax:
        raise ValueError("lmax value too small")

    blm = np.zeros((ncomp, nval), dtype=np.complex128)
    sigmasq = fwhm * fwhm / (8 * np.log(2.0))

    for l in range(lmax+1):
        blm[0, hp.Alm.getidx(lmax, l, 0)] = np.sqrt((2*l+1) / (4*np.pi)) \
            * np.exp(-0.5*sigmasq*l*(l+1))

    if pol:
        for l in range(2, lmax+1):
            blm[1, hp.Alm.getidx(lmax, l, 2)] = np.sqrt((2*l+1) / (4*np.pi)) \
                * np.exp(-0.5 * sigmasq * (l*(l+1)-4))
        blm[2] = 1j * blm[1]

    return blm

def make_full_random_alm(lmax, mmax, rng):
    res = rng.uniform(-1., 1., (4, nalm(lmax, mmax))) \
     + 1j*rng.uniform(-1., 1., (4, nalm(lmax, mmax)))
    # make a_lm with m==0 real-valued
    res[:, 0:lmax+1].imag = 0.
    ofs=0
    # components 1 and 2 are spin-2, fix them accordingly
    spin=2
    for s in range(spin):
        res[1:3, ofs:ofs+spin-s] = 0.
        ofs += lmax+1-s
    return res

np.random.seed(10)
rng = np.random.default_rng(np.random.SeedSequence(42))

# completely random sky
slm =make_full_random_alm(lmax, lmax, rng).real

# completely random Mueller matrix
mueller = np.random.uniform(-1,1,size=(4,4))

blm = make_full_random_alm(lmax, kmax, rng).real

# completely random pointings
ptg = np.empty((nptg,3))
ptg[:,0]=np.random.uniform(0,np.pi,size=(nptg,))          # theta
ptg[:,1]=np.random.uniform(0,2*np.pi,size=(nptg,))        # phi
ptg[:,2]=np.random.uniform(0,2*np.pi,size=(nptg,))        # psi
hwp_angles = np.random.uniform(0,2*np.pi,size=(nptg,))    # alpha

# Now do the same thing with MuellerConvolver
fullconv = mc.MuellerConvolver(
    lmax=lmax,
    kmax=kmax,
    slm=slm,
    blm=blm,
    mueller=mueller,
    single_precision=False,
    epsilon=1e-7,
    nthreads=nthreads
)


signal_muellerconvolver = fullconv.signal(ptg=ptg, alpha=hwp_angles)

end = time.time()  # end time

time_diff = end - start  
print(time_diff) 

np.save(f"test_tod=lmax{lmax}=kmax{kmax}=vnode{vnode}=vcore{vcore}=vnode_mem{vnode_mem}", signal_muellerconvolver)
