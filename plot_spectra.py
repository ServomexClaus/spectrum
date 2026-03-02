from pathlib import Path
from typing import Optional

import matplotlib
import numpy as np
from matplotlib.widgets import CheckButtons


def configure_interactive_backend() -> None:
    forced_backend = matplotlib.get_backend().lower()
    if "agg" not in forced_backend:
        return

    for candidate_backend in ("TkAgg", "QtAgg", "Qt5Agg"):
        try:
            matplotlib.use(candidate_backend, force=True)
            return
        except Exception:
            continue


configure_interactive_backend()

import matplotlib.pyplot as plt


def resolve_file(base_dir: Path, primary_name: str, fallback_name: Optional[str] = None) -> Path:
    primary_path = base_dir / primary_name
    if primary_path.exists():
        return primary_path

    if fallback_name is not None:
        fallback_path = base_dir / fallback_name
        if fallback_path.exists():
            return fallback_path

    missing = [primary_name] + ([fallback_name] if fallback_name else [])
    raise FileNotFoundError(f"Could not find any of these files: {', '.join(missing)}")


def load_spectrum(file_path: Path) -> tuple[np.ndarray, np.ndarray]:
    wavelength_values: list[float] = []
    absorption_values: list[float] = []

    with file_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue

            parts = line.replace(",", " ").split()
            if len(parts) < 2:
                continue

            try:
                wavelength = float(parts[0])
                absorption = float(parts[1])
            except ValueError:
                continue

            wavelength_values.append(wavelength)
            absorption_values.append(absorption)

    if not wavelength_values:
        raise ValueError(f"No valid 2-column numeric rows found in {file_path.name}")

    wavelength_nm = np.asarray(wavelength_values, dtype=float)
    absorption = np.asarray(absorption_values, dtype=float)
    return wavelength_nm, absorption


def main() -> None:
    base_dir = Path(__file__).resolve().parent

    gas_prefix_by_code = {
        "02": "He",
        "07": "N2",
        "08": "O2",
        "18": "Ar",
    }
    gas_colors = {
        "Ar": "lightgreen",
        "O2": "cyan",
        "N2": "yellow",
        "He": "tan",
    }
    source_styles = {
        "Kurucz": {"linestyle": "-", "linewidth": 1.0},
        "NIST": {"linestyle": "-", "linewidth": 1.0},
    }
    source_order = {"Kurucz": 0, "NIST": 1}

    spectrum_entries: list[tuple[str, Path, dict[str, object]]] = []
    for asc_file in sorted(base_dir.glob("*.asc")):
        parts = asc_file.stem.split("_", 1)
        if len(parts) != 2:
            continue

        code, source = parts
        prefix = gas_prefix_by_code.get(code)
        style = source_styles.get(source)
        if prefix is None or style is None:
            continue

        label = f"{prefix}_{source}"
        spectrum_entries.append((label, asc_file, style))

    spectrum_entries.sort(
        key=lambda entry: (
            next((code for code, prefix in gas_prefix_by_code.items() if entry[0].startswith(f"{prefix}_")), "99"),
            source_order.get(entry[0].split("_", 1)[1], 99),
        )
    )

    if not spectrum_entries:
        raise FileNotFoundError("No matching ASC files found for codes 02, 07, 08, or 18.")

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.subplots_adjust(right=0.78)

    plotted_series = []
    for label, file_path, style in spectrum_entries:
        wavelength_nm, absorption = load_spectrum(file_path)
        gas_prefix = label.split("_", 1)[0]
        line_color = gas_colors.get(gas_prefix)
        line, = ax.plot(wavelength_nm, absorption, label=label, color=line_color, **style)
        plotted_series.append((label, line))

    ax.set_title("Spectra Comparison")
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Absorption")
    ax.set_xlim(0, 1000)
    ax.legend(loc="upper left")
    ax.grid(alpha=0.3)

    checkbox_ax = fig.add_axes([0.80, 0.22, 0.18, 0.56])
    labels = [label for label, _ in plotted_series]
    visibility = [line.get_visible() for _, line in plotted_series]
    check = CheckButtons(checkbox_ax, labels, visibility)
    checkbox_ax.set_title("Show / Hide")

    def toggle_series(selected_label: Optional[str]) -> None:
        if selected_label is None:
            return

        for label, line in plotted_series:
            if label == selected_label:
                line.set_visible(not line.get_visible())
                break
        fig.canvas.draw_idle()

    check.on_clicked(toggle_series)

    plt.show()


if __name__ == "__main__":
    main()
