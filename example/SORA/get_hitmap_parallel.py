import litebird_sim as lbs
import healpy as hp
import numpy as np
import matplotlib.pylab as plt
import astropy.units as u
from mpi4py import MPI

comm = lbs.MPI_COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
print("Hello world: rank {} of {}".format(rank, size))

sim = lbs.Simulation(
    base_path   = "./get_hitmap_parallel",
    name        = "Parallel simulation tutorial",
    start_time  = 0,
    duration_s  = 86400.,
    random_seed = 12345,
    mpi_comm    = comm,
)

alpha           = 45.
beta            = 50.
spin_rpm        = 0.05
prec_period_min = 192.348

sim.set_scanning_strategy(
    scanning_strategy      = lbs.SpinningScanningStrategy(
        spin_sun_angle_rad = np.deg2rad(alpha), 
        spin_rate_hz       = spin_rpm / 60, 
        precession_rate_hz = 1.0 / (prec_period_min * u.min).to("s").value,
    )
)

sim.set_instrument(
    lbs.InstrumentInfo(
        name = "Satellite",
        spin_boresight_angle_rad = np.deg2rad(beta),
    ),
)

sim.set_hwp(lbs.IdealHWP(ang_speed_radpsec = 0.0))

det_list = [
    lbs.DetectorInfo(
        name             = "Detector1",
        sampling_rate_hz = 1,
        quat             = [0.02, 0.07, 0., 0.9]
    ),
    lbs.DetectorInfo(
        name             = "Detector2",
        sampling_rate_hz = 1,
        quat             = [0.02, -0.07, 0., 0.9]
    ),
]

print("Create observation")
(obs,) = sim.create_observations(
    detectors     = det_list,
    n_blocks_det  = 1,
    n_blocks_time = size,
    split_list_over_processes = False
)

inst = lbs.InstrumentInfo(
	name = "Telescope", 
	boresight_rotangle_rad   = 0.,
	spin_boresight_angle_rad = np.deg2rad(beta),
	spin_rotangle_rad        = 0.,
)

comm.barrier()
pointings = lbs.pointings.get_pointings(
	obs,
	spin2ecliptic_quats    = sim.spin2ecliptic_quats,
	bore2spin_quat         = inst.bore2spin_quat,
	store_pointings_in_obs = False    #if True, stores colatitude and longitude in obs.pointings and the polarization angle in obs.psi
)

comm.barrier()
print(f"rank: {rank}, pointing shape: {pointings.shape}")

nside  = 128
npix   = hp.nside2npix(nside)
if(rank==0):
    hitmap = np.zeros(npix)
else:
    hitmap = None

hitmap = comm.bcast(hitmap, root=0)    
for i_det in range(len(det_list)):
    pixels = hp.ang2pix(nside,
                        pointings[i_det][:,0], #theta
                        pointings[i_det][:,1]  #phi
                       ) 
    for ipix in pixels:
        hitmap[ipix] += 1

comm.barrier()
hitmap = comm.allreduce(hitmap, op=MPI.SUM)

print(f"Gathered hitmap has {hitmap} as total hits.")
if(rank==0):
    hp.mollview(hitmap)
    hp.write_map(sim.base_path / 'hitmap.fits', hitmap, overwrite=True, dtype=np.int64)


    sim.append_to_report("""

    ## Coverage map

    Here is the coverage map:

    ![](coverage_map.png)

    The fraction of sky covered is {{ seen }}/{{ total }} pixels
    ({{ "%.1f" | format(percentage) }}%).

    The total number of hit is {{total_hit}}
    """,
        figures    = [(plt.gcf(), "coverage_map.png")],
        seen       = len(hitmap[hitmap > 0]),
        total      = len(hitmap),
        percentage = 100.0 * len(hitmap[hitmap > 0]) / len(hitmap),
        total_hit  = hitmap.sum()
    )

    sim.flush()