import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import os

np.random.seed (42)

RHO = 1.0
NU = 0.01
L = 1.0
H = 0.1
U_MAX = 1.0

N_POINTS_X = 20
N_POINTS_Y = 10
N_TIME = 10
DT = 0.01

x = np.linspace (0, L, N_POINTS_X)
y = np.linspace (0, H, N_POINTS_Y)
t = np.linspace (0, N_TIME * DT, N_TIME)
X, Y = np.meshgrid (x, y, indexing='ij')

MAX_WORKERS = 4
CHUNK_SIZE = 20


def poiseuille_flow(y, h, u_max, nu):
    """Analytical solution for laminar Poiseuille flow between two plates."""
    return 4 * u_max * y * (h - y) / (h ** 2)


def compute_derivatives_3d(u, v, x, y, t, dx, dy, dt):
    """Compute spatial and temporal derivatives for Navier-Stokes over all time steps."""
    N_TIME, N_POINTS_X, N_POINTS_Y = u.shape
    dudx = np.zeros_like (u)
    dudy = np.zeros_like (u)
    dvdx = np.zeros_like (v)
    dvdy = np.zeros_like (v)
    dudt = np.zeros_like (u)
    dvdt = np.zeros_like (v)

    for t_idx in range (N_TIME):
        for i in range (1, N_POINTS_X - 1):
            for j in range (1, N_POINTS_Y - 1):
                dudx [t_idx, i, j] = (u [t_idx, i + 1, j] - u [t_idx, i - 1, j]) / (2 * dx)
                dudy [t_idx, i, j] = (u [t_idx, i, j + 1] - u [t_idx, i, j - 1]) / (2 * dy)
                dvdx [t_idx, i, j] = (v [t_idx, i + 1, j] - v [t_idx, i - 1, j]) / (2 * dx)
                dvdy [t_idx, i, j] = (v [t_idx, i, j + 1] - v [t_idx, i, j - 1]) / (2 * dy)

    for t_idx in range (N_TIME):
        if t_idx == 0:
            dudt [t_idx] = (u [t_idx + 1] - u [t_idx]) / dt
            dvdt [t_idx] = (v [t_idx + 1] - v [t_idx]) / dt
        elif t_idx == N_TIME - 1:
            dudt [t_idx] = (u [t_idx] - u [t_idx - 1]) / dt
            dvdt [t_idx] = (v [t_idx] - v [t_idx - 1]) / dt
        else:
            dudt [t_idx] = (u [t_idx + 1] - u [t_idx - 1]) / (2 * dt)
            dvdt [t_idx] = (v [t_idx + 1] - v [t_idx - 1]) / (2 * dt)

    return dudx, dudy, dvdx, dvdy, dudt, dvdt


def generate_flow_data(args):
    """Generate flow data for a single sample."""
    sample_id, flow_type, X, Y, x, y, t = args
    try:
        u = np.zeros ((N_TIME, N_POINTS_X, N_POINTS_Y))
        v = np.zeros_like (u)
        p = np.zeros_like (u)

        for j in range (N_POINTS_Y):
            u [0, :, j] = poiseuille_flow (y [j], H, U_MAX, NU)
            if flow_type == "turbulent":
                u [0, :, j] += np.random.normal (0, 0.1, N_POINTS_X)

        v [0] = np.random.normal (0, 0.05, u [0].shape) if flow_type == "turbulent" else np.random.normal (0, 0.001,
                                                                                                           u [0].shape)

        for t_idx in range (1, N_TIME):
            if flow_type == "laminar":
                u [t_idx] = u [0] + np.random.normal (0, 0.01, u [0].shape)  # Slight variation
                v [t_idx] = v [0] + np.random.normal (0, 0.001, v [0].shape)  # Ensure v remains non-zero
                p [t_idx] = -8 * NU * U_MAX / (H ** 2) * X + np.random.normal (0, 0.01, X.shape)
            else:
                if t_idx > 1:
                    dudx_prev, dudy_prev, dvdx_prev, dvdy_prev, _, _ = compute_derivatives_3d (
                        u [:t_idx], v [:t_idx], x, y, t [:t_idx], x [1] - x [0], y [1] - y [0], DT
                    )
                    u [t_idx] = u [t_idx - 1] + DT * (
                            -u [t_idx - 1] * dudx_prev [-1] - v [t_idx - 1] * dudy_prev [-1] +
                            NU * (dudx_prev [-1] + dudy_prev [-1])
                    )
                    v [t_idx] = v [t_idx - 1] + DT * (
                            -u [t_idx - 1] * dvdx_prev [-1] - v [t_idx - 1] * dvdy_prev [-1] +
                            NU * (dvdx_prev [-1] + dvdy_prev [-1])
                    )
                else:
                    u [t_idx] = u [t_idx - 1] + np.random.normal (0, 0.05, u [t_idx].shape)
                    v [t_idx] = v [t_idx - 1] + np.random.normal (0, 0.05, v [t_idx].shape)
                p [t_idx] = -RHO * (u [t_idx] ** 2 + v [t_idx] ** 2) / 2
                u [t_idx] += np.random.normal (0, 0.05, u [t_idx].shape)
                v [t_idx] += np.random.normal (0, 0.05, v [t_idx].shape)

        dx = x [1] - x [0]
        dy = y [1] - y [0]
        dudx, dudy, dvdx, dvdy, dudt, dvdt = compute_derivatives_3d (u, v, x, y, t, dx, dy, DT)

        T, X_local, Y_local = np.meshgrid (t, x, y, indexing='ij')
        data = {
            't': T.ravel (),
            'x': X_local.ravel (),
            'y': Y_local.ravel (),
            'u': u.ravel (),
            'v': v.ravel (),
            'p': p.ravel (),
            'dudx': dudx.ravel (),
            'dudy': dudy.ravel (),
            'dvdx': dvdx.ravel (),
            'dvdy': dvdy.ravel (),
            'dudt': dudt.ravel (),
            'dvdt': dvdt.ravel (),
            'flow_type': flow_type,
            'sample_id': sample_id
        }
        df = pd.DataFrame (data)

        df = df [(df ['u'] != 0) & (df ['v'] != 0)]

        return df

    except Exception as e:
        print (f"Error processing sample {sample_id} ({flow_type}): {str (e)}")
        return None


def batch_generate_flow(samples, X, Y, x, y, t):
    """Generate flow data in parallel for a batch of samples."""
    all_data = []
    with ThreadPoolExecutor (max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit (generate_flow_data, (sample_id, flow_type, X, Y, x, y, t))
                   for sample_id, flow_type in samples]
        for future in tqdm (as_completed (futures), total=len (futures), desc="Generating Flow Data"):
            result = future.result ()
            if result is not None:
                all_data.append (result)
    successful = len (all_data)
    failed = len (samples) - successful
    return all_data, successful, failed


def main():
    """Main function to generate and save flow data."""
    try:
        n_samples_laminar = 100
        n_samples_turbulent = 100
        laminar_samples = [(i, "laminar") for i in range (n_samples_laminar)]
        turbulent_samples = [(i + n_samples_laminar, "turbulent") for i in range (n_samples_turbulent)]
        all_samples = laminar_samples + turbulent_samples

        chunks = [all_samples [i:i + CHUNK_SIZE] for i in range (0, len (all_samples), CHUNK_SIZE)]
        total_successful = 0
        total_failed = 0
        all_dataframes = []

        for chunk in tqdm (chunks, desc="Processing chunks"):
            dataframes, successful, failed = batch_generate_flow (chunk, X, Y, x, y, t)
            total_successful += successful
            total_failed += failed
            if dataframes:
                all_dataframes.extend (dataframes)

        if all_dataframes:
            combined_df = pd.concat (all_dataframes, ignore_index=True)
            laminar_df = combined_df [combined_df ['flow_type'] == 'laminar']
            turbulent_df = combined_df [combined_df ['flow_type'] == 'turbulent']

            print (f"Laminar rows available: {len (laminar_df)}")
            print (f"Turbulent rows available: {len (turbulent_df)}")

            laminar_sampled = laminar_df.sample (n=5000, replace=True, random_state=42) if len (
                laminar_df) > 0 else pd.DataFrame ()
            turbulent_sampled = turbulent_df.sample (n=5000, replace=True, random_state=42) if len (
                turbulent_df) > 0 else pd.DataFrame ()

            final_df = pd.concat ([laminar_sampled, turbulent_sampled], ignore_index=True)
            if len (final_df) == 10000:
                final_df.to_csv ("Flow.csv", index=False)
                print (f"\n✅ Dataset saved to: {os.path.abspath ('Flow.csv')}")
                print (f"Dataset size: {len (final_df)} rows (5,000 laminar, 5,000 turbulent)")
            else:
                print (f"\n❌ Insufficient data after sampling: {len (final_df)} rows generated.")
        else:
            print ("\n❌ No data generated.")

        print ("\n✅ Generation Summary:")
        print (f"Successfully generated samples: {total_successful}")
        print (f"Failed samples: {total_failed}")
        print (f"Total samples processed: {total_successful + total_failed}")

    except Exception as e:
        print (f"❌ Error: {str (e)}")


if __name__ == "__main__":
    main ()
