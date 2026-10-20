#!/usr/bin/env python3
"""
=======================================================================
ANALYSIS PIPELINE: Fifth-Order Azimuthal Perturbation in NGC 628
=======================================================================
Companion code to:
  "Fifth-Order Azimuthal Perturbation in the HI Velocity Field of NGC 628:
   Detection, Validation, and Observational Constraints"

Authors: [Nome da Autora]
Date: June 2026

Requirements:
  numpy, scipy, matplotlib, scikit-learn

Data:
  THINGS moment-1 FITS files (public domain):
  https://www2.mpia-hd.mpg.de/THINGS/Data.html
  
  Files used:
    NGC_628_NA_MOM1_THINGS.FITS
    NGC_628_RO_MOM1_THINGS.FITS
    NGC_3184_NA_MOM1_THINGS.FITS
    NGC_3184_RO_MOM1_THINGS.FITS
    NGC_5457_NA_MOM1_THINGS.FITS
    NGC_5457_RO_MOM1_THINGS.FITS
=======================================================================
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import eigsh
import warnings
warnings.filterwarnings('ignore')

# ════════════════════════════════════════════════════════════════
# SECTION 1: FITS READER (no astropy dependency)
# ════════════════════════════════════════════════════════════════

def read_fits_moment1(filepath, v_min_kms, v_max_kms):
    """
    Read a THINGS moment-1 FITS file without astropy.
    Returns velocity field (km/s), valid pixel mask, and header dict.
    
    Parameters
    ----------
    filepath : str
        Path to FITS file (moment-1, BUNIT=METR/SEC)
    v_min_kms, v_max_kms : float
        Valid velocity range in km/s
        
    Returns
    -------
    v_kms : 2D ndarray
        Velocity field in km/s (NaN outside valid range)
    mask : 2D bool ndarray
        True where data is valid
    header : dict
        FITS header key-value pairs
    """
    with open(filepath, 'rb') as f:
        raw = f.read()
    
    header = {}
    pos = 0
    while pos < len(raw):
        block = raw[pos:pos+2880]
        for i in range(36):
            card = block[i*80:(i+1)*80].decode('ascii', errors='replace')
            key = card[:8].strip()
            if key == 'END':
                data_start = pos + 2880
                nx = int(header['NAXIS1'])
                ny = int(header['NAXIS2'])
                data = np.frombuffer(
                    raw[data_start:data_start+nx*ny*4],
                    dtype='>f4'
                ).astype(np.float64).reshape(ny, nx) / 1000.0  # m/s → km/s
                mask = (data > v_min_kms) & (data < v_max_kms) & np.isfinite(data)
                data[~mask] = np.nan
                return data, mask, header
            if '=' in card:
                val = card[8:].split('/')[0].replace('=','').strip().strip("'").strip()
                header[key] = val
        pos += 2880
    raise ValueError("FITS END card not found")


# ════════════════════════════════════════════════════════════════
# SECTION 2: COORDINATE TRANSFORMATION
# ════════════════════════════════════════════════════════════════

def sky_to_galactic_plane(header, inc_deg, pa_deg, dist_Mpc):
    """
    Convert pixel coordinates to galactic-plane polar coordinates (R_kpc, psi).
    Uses tilted-ring projection.
    
    Parameters
    ----------
    header : dict
        FITS header (needs NAXIS1/2, CRPIX1/2, CDELT1/2)
    inc_deg : float
        Disk inclination in degrees
    pa_deg : float
        Position angle (E of N) in degrees
    dist_Mpc : float
        Distance in Mpc
        
    Returns
    -------
    R_kpc : 2D ndarray
        Galactocentric radius in kpc
    psi : 2D ndarray
        Azimuthal angle in galactic plane (radians)
    """
    nx = int(header['NAXIS1']); ny = int(header['NAXIS2'])
    crpix1 = float(header['CRPIX1']); crpix2 = float(header['CRPIX2'])
    cdelt1 = float(header['CDELT1'])
    cdelt2 = abs(float(header.get('CDELT2', str(abs(float(header['CDELT1']))))))
    
    kpc_per_deg = dist_Mpc * 1000.0 * np.pi / 180.0
    ix = np.arange(nx); iy = np.arange(ny)
    IX, IY = np.meshgrid(ix, iy)
    
    dRA  = (IX - (crpix1-1)) * cdelt1
    dDec = (IY - (crpix2-1)) * cdelt2
    x_kpc = dRA  * kpc_per_deg
    y_kpc = dDec * kpc_per_deg
    
    PA_rad  = np.radians(pa_deg)
    inc_rad = np.radians(inc_deg)
    
    X_maj =  x_kpc * np.sin(PA_rad) + y_kpc * np.cos(PA_rad)
    X_min = -x_kpc * np.cos(PA_rad) + y_kpc * np.sin(PA_rad)
    
    X_gal = X_maj
    Y_gal = X_min / np.cos(inc_rad)
    
    R_kpc = np.sqrt(X_gal**2 + Y_gal**2)
    psi   = np.arctan2(Y_gal, X_gal)
    
    return R_kpc, psi


# ════════════════════════════════════════════════════════════════
# SECTION 3: FOURIER AZIMUTHAL DECOMPOSITION
# ════════════════════════════════════════════════════════════════

def fourier_decomposition(v_los, R_kpc, psi, mask, r_bins, inc_deg, v_sys, N=10):
    """
    Decompose the velocity field into azimuthal Fourier modes for each
    radial ring:
    
      V_los(r,psi) = V_sys + V_rot(r)*sin(i)*cos(psi)
                   + sum_{n=1}^{N} [c_n(r)*cos(n*psi) + s_n(r)*sin(n*psi)]
    
    Parameters
    ----------
    v_los : 2D ndarray
        Line-of-sight velocity field (km/s)
    R_kpc, psi : 2D ndarrays
        Galactocentric radius and azimuthal angle
    mask : 2D bool ndarray
        Valid pixel mask
    r_bins : 1D ndarray
        Radial bin centres (kpc)
    inc_deg : float
        Inclination in degrees
    v_sys : float
        Systemic velocity (km/s)
    N : int
        Maximum harmonic order (default 10)
        
    Returns
    -------
    results : dict
        Keys: 'r', 'n_pts', 'V_rot', and for each n=1..N: 'c{n}', 's{n}', 'A{n}', 'theta{n}'
    """
    sin_i = np.sin(np.radians(inc_deg))
    dr    = (r_bins[1] - r_bins[0]) / 2.0
    
    res = {'r': [], 'n_pts': [], 'V_rot': []}
    for n in range(1, N+1):
        res[f'c{n}'] = []; res[f's{n}'] = []
        res[f'A{n}'] = []; res[f'theta{n}'] = []
    
    for r_c in r_bins:
        in_ring = mask & (np.abs(R_kpc - r_c) < dr) & np.isfinite(v_los)
        n_pts   = int(np.sum(in_ring))
        res['r'].append(r_c); res['n_pts'].append(n_pts)
        
        if n_pts < 2*N + 4:
            res['V_rot'].append(np.nan)
            for n in range(1, N+1):
                res[f'c{n}'].append(np.nan); res[f's{n}'].append(np.nan)
                res[f'A{n}'].append(np.nan); res[f'theta{n}'].append(np.nan)
            continue
        
        psi_r = psi[in_ring]; v_r = v_los[in_ring]
        
        # Design matrix: [sin(i)*cos(psi), cos(psi), sin(psi), ..., cos(N*psi), sin(N*psi)]
        A_mat = np.zeros((n_pts, 1 + 2*N))
        A_mat[:, 0] = sin_i * np.cos(psi_r)
        for n in range(1, N+1):
            A_mat[:, 2*n-1] = np.cos(n * psi_r)
            A_mat[:, 2*n]   = np.sin(n * psi_r)
        
        coeffs, _, _, _ = np.linalg.lstsq(A_mat, v_r - v_sys, rcond=None)
        
        res['V_rot'].append(coeffs[0])  # V_rot * sin(i) absorbed
        for n in range(1, N+1):
            cn = coeffs[2*n-1]; sn = coeffs[2*n]
            res[f'c{n}'].append(cn); res[f's{n}'].append(sn)
            res[f'A{n}'].append(np.sqrt(cn**2 + sn**2))
            res[f'theta{n}'].append(np.arctan2(sn, cn))
    
    for key in res:
        res[key] = np.array(res[key])
    return res


# ════════════════════════════════════════════════════════════════
# SECTION 4: STATISTICAL TESTS
# ════════════════════════════════════════════════════════════════

def robust_Z_score(fourier_results, test_mode=5, zone_r=(9, 14)):
    """
    Z-score of mode m=test_mode against multi-mode baseline.
    
    Z = (mean(A_5) - mean(A_baseline)) / (std(A_baseline) / sqrt(N_rings))
    
    Baseline: all modes n=2..10 except test_mode.
    
    Parameters
    ----------
    fourier_results : dict
        Output of fourier_decomposition()
    test_mode : int
        Mode to test (default 5)
    zone_r : tuple
        (r_lo, r_hi) defining the stable zone in kpc
        
    Returns
    -------
    dict with Z, mean_test, mean_base, std_base, N_rings
    """
    r = fourier_results['r']
    n_pts = fourier_results['n_pts']
    zone = (r >= zone_r[0]) & (r <= zone_r[1]) & (n_pts > 50)
    
    A_test = fourier_results[f'A{test_mode}'][zone]
    baseline_modes = [m for m in range(2, 11) if m != test_mode]
    A_base = np.concatenate([fourier_results[f'A{m}'][zone] for m in baseline_modes])
    
    mean_test = np.nanmean(A_test)
    mean_base = np.nanmean(A_base)
    std_base  = np.nanstd(A_base)
    N_rings   = int(np.sum(zone))
    
    Z = (mean_test - mean_base) / (std_base / np.sqrt(N_rings))
    
    return {'Z': Z, 'mean_test': mean_test, 'mean_base': mean_base,
            'std_base': std_base, 'N_rings': N_rings}


def phase_coherence(fourier_results, mode=5, zone_r=(9, 14), n_pts_min=50):
    """
    Mean resultant length (circular coherence) of phase theta_m(r):
      C_phi = |mean(exp(i * theta_m(r)))|
    
    Returns C_phi and p-value under circular null theta ~ U[0, 2*pi].
    """
    r     = fourier_results['r']
    n_pts = fourier_results['n_pts']
    zone  = (r >= zone_r[0]) & (r <= zone_r[1]) & (n_pts > n_pts_min)
    
    theta = fourier_results[f'theta{mode}'][zone]
    theta = theta[~np.isnan(theta)]
    N = len(theta)
    if N < 3:
        return {'C_phi': np.nan, 'p_circ': np.nan, 'Z_circ': np.nan, 'N': N}
    
    C_obs = float(np.abs(np.mean(np.exp(1j * theta))))
    
    # Circular null: N=5000 permutations
    np.random.seed(42)
    null = np.array([
        float(np.abs(np.mean(np.exp(1j * np.random.uniform(0, 2*np.pi, N)))))
        for _ in range(5000)
    ])
    p = float((1 + np.sum(null >= C_obs)) / (1 + len(null)))
    Z = float((C_obs - null.mean()) / null.std())
    
    return {'C_phi': C_obs, 'p_circ': p, 'Z_circ': Z, 'N': N,
            'null_mean': float(null.mean()), 'null_std': float(null.std())}


def bootstrap_A5(v_los, R_kpc, psi, mask, r_bins, inc_deg, v_sys,
                 zone_r=(9, 14), B=500, seed=42):
    """
    Bootstrap confidence interval for mean(A5) in the stable zone.
    Resamples pixels within each ring independently.
    Returns IC 95% [lo, hi] and bootstrap distribution.
    """
    np.random.seed(seed)
    dr = (r_bins[1] - r_bins[0]) / 2.0
    sin_i = np.sin(np.radians(inc_deg))
    N = 5  # only need up to mode 5
    
    # Collect ring data first
    ring_data = []
    for r_c in r_bins:
        if r_c < zone_r[0] or r_c > zone_r[1]:
            continue
        in_ring = mask & (np.abs(R_kpc - r_c) < dr) & np.isfinite(v_los)
        if np.sum(in_ring) < 2*N+4:
            continue
        ring_data.append((psi[in_ring], v_los[in_ring]))
    
    boot_A5 = []
    for _ in range(B):
        A5_per_ring = []
        for psi_r, v_r in ring_data:
            idx = np.random.choice(len(v_r), len(v_r), replace=True)
            A_mat = np.zeros((len(idx), 1+2*N))
            A_mat[:,0] = sin_i * np.cos(psi_r[idx])
            for n in range(1, N+1):
                A_mat[:,2*n-1] = np.cos(n*psi_r[idx])
                A_mat[:,2*n]   = np.sin(n*psi_r[idx])
            try:
                coeffs, _, _, _ = np.linalg.lstsq(A_mat, v_r[idx]-v_sys, rcond=None)
                A5_per_ring.append(np.sqrt(coeffs[9]**2 + coeffs[10]**2))
            except:
                pass
        if A5_per_ring:
            boot_A5.append(np.mean(A5_per_ring))
    
    boot_A5 = np.array(boot_A5)
    return {
        'boot_A5': boot_A5,
        'IC95_lo': float(np.percentile(boot_A5, 2.5)),
        'IC95_hi': float(np.percentile(boot_A5, 97.5)),
        'mean': float(np.mean(boot_A5)),
        'std':  float(np.std(boot_A5)),
    }


def leakage_test(fourier_results, zone_r=(9, 14), n_pts_min=50):
    """
    Pearson correlation between A5(r) and propagated error of V_rot(r).
    High correlation (r > 0.6) indicates A5 is a fitting artefact.
    """
    from scipy import stats
    r = fourier_results['r']; n_pts = fourier_results['n_pts']
    zone = (r >= zone_r[0]) & (r <= zone_r[1]) & (n_pts > n_pts_min)
    
    A5 = fourier_results['A5'][zone]
    # Proxy for err(V_rot): use A5 residuals standard deviation
    # (exact propagated error requires the full covariance matrix per ring)
    # Here we use a simplified proxy: A1 = V_rot * sin(i) / sqrt(n_ring)
    V_rot = np.abs(fourier_results['V_rot'][zone])
    n_r   = n_pts[zone].astype(float)
    err_vrot_proxy = V_rot / np.sqrt(n_r + 1e-10)
    
    ok = ~np.isnan(A5) & ~np.isnan(err_vrot_proxy)
    if np.sum(ok) < 3:
        return {'r': np.nan, 'p': np.nan}
    
    r_corr, p_corr = stats.pearsonr(A5[ok], err_vrot_proxy[ok])
    return {'r': float(r_corr), 'p': float(p_corr)}


# ════════════════════════════════════════════════════════════════
# SECTION 5: MAIN ANALYSIS PIPELINE
# ════════════════════════════════════════════════════════════════

# Galaxy parameters (de Blok et al. 2008)
GALAXY_PARAMS = {
    'NGC 628':  {'inc':7.,'pa':25.,'dist':7.3,'vsys':657.,
                  'v_min':550,'v_max':800,'zone':(9,14),
                  'na_file':'NGC_628_NA_MOM1_THINGS.FITS',
                  'ro_file':'NGC_628_RO_MOM1_THINGS.FITS'},
    'NGC 3184': {'inc':16.,'pa':179.,'dist':11.1,'vsys':592.,
                  'v_min':530,'v_max':660,'zone':(7,12),
                  'na_file':'NGC_3184_NA_MOM1_THINGS.FITS',
                  'ro_file':'NGC_3184_RO_MOM1_THINGS.FITS'},
    'NGC 5457': {'inc':18.,'pa':39.,'dist':7.4,'vsys':241.,
                  'v_min':100,'v_max':420,'zone':(9,16),
                  'na_file':'NGC_5457_NA_MOM1_THINGS.FITS',
                  'ro_file':'NGC_5457_RO_MOM1_THINGS.FITS'},
}

def run_full_analysis(fits_dir='.'):
    """
    Run the complete analysis pipeline for all galaxies.
    
    Parameters
    ----------
    fits_dir : str
        Directory containing THINGS FITS files
        
    Returns
    -------
    all_results : dict
        Results for each galaxy
    """
    all_results = {}
    
    for gname, gp in GALAXY_PARAMS.items():
        print(f"\nProcessing {gname} (i={gp['inc']}°)...")
        
        na_path = f"{fits_dir}/{gp['na_file']}"
        ro_path = f"{fits_dir}/{gp['ro_file']}"
        
        # Load data
        vna, mna, hna = read_fits_moment1(na_path, gp['v_min'], gp['v_max'])
        vro, mro, hro = read_fits_moment1(ro_path, gp['v_min'], gp['v_max'])
        
        vsys = float(np.nanmedian(vna[mna]))
        print(f"  v_sys = {vsys:.1f} km/s (lit: {gp['vsys']} km/s)")
        
        # Coordinate transformation
        R_kpc, psi = sky_to_galactic_plane(hna, gp['inc'], gp['pa'], gp['dist'])
        
        # Fourier decomposition
        r_bins = np.linspace(gp['zone'][0]-2, gp['zone'][1]+2, 30)
        fourier_na = fourier_decomposition(vna, R_kpc, psi, mna, r_bins,
                                            gp['inc'], vsys, N=10)
        fourier_ro = fourier_decomposition(vro, R_kpc, psi, mro, r_bins,
                                            gp['inc'], vsys, N=10)
        
        # Statistical tests
        Z_result = robust_Z_score(fourier_na, test_mode=5, zone_r=gp['zone'])
        Cphi_result = phase_coherence(fourier_na, mode=5, zone_r=gp['zone'])
        leak_result = leakage_test(fourier_na, zone_r=gp['zone'])
        
        print(f"  Z_robust(m=5) = {Z_result['Z']:.2f}")
        print(f"  C_phi,5       = {Cphi_result['C_phi']:.4f}  p={Cphi_result['p_circ']:.4f}")
        print(f"  Leakage r     = {leak_result['r']:.3f}  p={leak_result['p']:.3f}")
        
        all_results[gname] = {
            'fourier_na': fourier_na,
            'fourier_ro': fourier_ro,
            'Z_A5': Z_result,
            'C_phi': Cphi_result,
            'leakage': leak_result,
            'v_sys': vsys,
            'R_kpc': R_kpc,
            'psi': psi,
        }
    
    return all_results


if __name__ == '__main__':
    import sys
    fits_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    print(f"THINGS FITS directory: {fits_dir}")
    results = run_full_analysis(fits_dir)
    print("\nDone. Results available in 'results' dict.")
    print("Key results:")
    for gname, res in results.items():
        Z = res['Z_A5']['Z']; C = res['C_phi']['C_phi']; p = res['C_phi']['p_circ']
        print(f"  {gname}: Z={Z:.2f}  C_phi={C:.4f}  p={p:.4f}")
