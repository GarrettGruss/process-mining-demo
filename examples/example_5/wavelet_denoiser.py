"""WaveletDenoiser: signal cleaning and energy-based change detection (stretch goal).

Requires: pywt (PyWavelets)  →  pip install PyWavelets

This class uses a single wavelet decomposition to both clean noisy sensor channels and
detect structural change points, replacing the ruptures-based detect_change_points()
from example_4.  Entries in SHIP_EVENTS that specify method="detect_energy_change_points"
are routed to this class by the SHIP dispatcher.
"""

import warnings

import numpy as np
import pandas as pd


class WaveletDenoiser:
    """Wavelet-based denoising and energy change detection for telemetry channels.

    Example:
        wd = WaveletDenoiser(df, wavelet="db4", level=4)
        denoised_df = wd.denoise_all(["f88.ect1_°f", "f88.oil.p1_psi"])
        events = wd.detect_energy_change_points(
            column="f88.ect1_°f",
            event_name="engine_temp_energy_change",
            threshold_sigma=3.0,
        )
    """

    def __init__(self, df: pd.DataFrame, wavelet: str = "db4", level: int = 4):
        """Initialise with a telemetry DataFrame.

        Args:
            df:      Telemetry DataFrame with a 'time.absolute' column.
            wavelet: PyWavelets wavelet name (e.g. "db4", "sym5", "haar").
            level:   Decomposition level.  Higher = coarser frequency resolution.
                     Must satisfy level <= log2(len(signal)).  Set to None to use
                     the maximum supported level.
        """
        try:
            import pywt  # noqa: F401
        except ImportError as exc:
            raise ImportError(
                "PyWavelets is required for WaveletDenoiser.  "
                "Install it with: pip install PyWavelets"
            ) from exc

        self.df = df
        self.wavelet = wavelet
        self.level = level

    # ------------------------------------------------------------------
    # Denoising
    # ------------------------------------------------------------------

    def denoise_channel(self, column: str) -> pd.Series:
        """Denoise a single channel using wavelet soft-thresholding.

        Decompose the signal, apply Donoho–Johnstone universal threshold to detail
        coefficients, then reconstruct.  NaN values are filled with the channel mean
        before decomposition and restored afterwards.

        Args:
            column: Column name in self.df to denoise.

        Returns:
            Cleaned pd.Series with the same index as self.df[column].
        """
        import pywt

        signal = self.df[column].copy()
        nan_mask = signal.isna()
        signal_filled = signal.fillna(signal.mean())
        values = signal_filled.values.astype(float)

        level = self.level or pywt.dwt_max_level(len(values), self.wavelet)
        coeffs = pywt.wavedec(values, self.wavelet, level=level)

        # Universal threshold: sigma * sqrt(2 * log(n))
        sigma = np.median(np.abs(coeffs[-1])) / 0.6745
        threshold = sigma * np.sqrt(2 * np.log(len(values)))

        denoised_coeffs = [coeffs[0]] + [
            pywt.threshold(c, threshold, mode="soft") for c in coeffs[1:]
        ]
        reconstructed = pywt.waverec(denoised_coeffs, self.wavelet)

        # waverec may add one extra sample; trim to original length
        reconstructed = reconstructed[: len(values)]

        result = pd.Series(reconstructed, index=self.df.index, name=column)
        result[nan_mask] = np.nan
        return result

    def denoise_all(self, columns: list[str]) -> pd.DataFrame:
        """Denoise multiple channels and return a DataFrame with the same shape.

        Args:
            columns: List of column names to denoise.  Columns not in self.df are skipped
                     with a warning.

        Returns:
            DataFrame containing only the denoised columns (same index as self.df).
        """
        result = {}
        for col in columns:
            if col not in self.df.columns:
                warnings.warn(f"[WaveletDenoiser] Column '{col}' not found — skipping.")
                continue
            result[col] = self.denoise_channel(col)
        return pd.DataFrame(result, index=self.df.index)

    # ------------------------------------------------------------------
    # Energy-based change detection
    # ------------------------------------------------------------------

    def compute_energy(self, column: str, window: int | None = None) -> pd.Series:
        """Compute windowed wavelet-coefficient energy for a channel.

        For each decomposition level, squares the detail coefficients and sums them
        within a sliding window, then up-samples back to the original time axis.
        The final energy series is the sum across all levels.

        Args:
            column: Channel to analyse.
            window: Sliding-window size (samples).  Defaults to 2^level, which aligns
                    with the coarsest decomposition level.

        Returns:
            Energy pd.Series aligned to self.df.index.
        """
        import pywt

        signal = self.df[column].fillna(self.df[column].mean()).values.astype(float)
        level = self.level or pywt.dwt_max_level(len(signal), self.wavelet)
        coeffs = pywt.wavedec(signal, self.wavelet, level=level)

        n = len(signal)
        win = window or 2**level
        energy = np.zeros(n)

        for detail in coeffs[1:]:
            # Upsample detail coefficients to original length
            upsampled = np.repeat(detail, max(1, n // len(detail)))[: n]
            # Pad if upsampling is short
            if len(upsampled) < n:
                upsampled = np.pad(upsampled, (0, n - len(upsampled)), mode="edge")

            squared = upsampled**2
            # Sliding window sum via cumsum
            cumsum = np.cumsum(np.insert(squared, 0, 0))
            windowed = (cumsum[win:] - cumsum[:-win]) / win
            # Align to original length
            pad = n - len(windowed)
            windowed = np.pad(windowed, (pad // 2, pad - pad // 2), mode="edge")
            energy += windowed

        return pd.Series(energy, index=self.df.index, name=f"{column}_energy")

    def detect_energy_change_points(
        self,
        column: str,
        event_name: str,
        threshold_sigma: float = 3.0,
    ) -> pd.DataFrame:
        """Detect structural change points via wavelet energy thresholding.

        Change points are identified as rising edges where the energy profile exceeds
        mean + threshold_sigma * std.  This replaces the ruptures-based approach:
        same goal (find structural transitions without manual value thresholds) but
        reuses the wavelet decomposition already computed for denoising.

        Output format matches EventClassifier methods (timestamp, activity, value).

        Args:
            column:          Channel to analyse.
            event_name:      Activity label for detected change points.
            threshold_sigma: How many standard deviations above the mean to threshold.

        Returns:
            DataFrame with columns: timestamp, activity, value.
        """
        if column not in self.df.columns:
            warnings.warn(
                f"[WaveletDenoiser] Column '{column}' not found — returning empty events."
            )
            return pd.DataFrame(columns=["timestamp", "activity", "value"])

        energy = self.compute_energy(column)
        threshold = energy.mean() + threshold_sigma * energy.std()
        above = energy > threshold

        rising_edge = above & ~above.shift(1, fill_value=False)
        event_indices = self.df[rising_edge].index

        return pd.DataFrame(
            {
                "timestamp": self.df.loc[event_indices, "time.absolute"].values,
                "activity": event_name,
                "value": energy.loc[event_indices].values,
            }
        ).reset_index(drop=True)
