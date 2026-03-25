# Project Guidelines

## Architecture
This workspace is centered on [plot_spectra.py](c:/Users/cagersbaek/spectrum/plot_spectra.py), a single Python entrypoint that loads local `.asc` spectral data files from the repository root and renders them with matplotlib.
Treat [index.html](c:/Users/cagersbaek/spectrum/index.html) as a minimal placeholder page unless the task is explicitly about the browser-facing UI.

## Build And Test
Install Python dependencies with `pip install numpy matplotlib`.
Run the main workflow with `python plot_spectra.py` from the repository root.
There is no automated test suite in this workspace. For behavior changes, prefer lightweight validation that does not rename or modify the checked-in data files.

## Conventions
Keep Python changes consistent with the existing style in [plot_spectra.py](c:/Users/cagersbaek/spectrum/plot_spectra.py): type hints, `pathlib.Path` for file handling, small focused functions, and dictionary-driven configuration for gases, colors, and source styles.
Preserve the current tolerance of `load_spectrum()` when parsing data files: blank lines, comma-separated values, and malformed rows are skipped rather than treated as fatal errors.
Preserve `configure_interactive_backend()` behavior unless the task specifically changes plotting/backends. Do not introduce backend assumptions that break local interactive plotting.

## Data Files
Spectral inputs live in the repository root and follow the `{code}_{source}.asc` naming pattern, such as `07_NIST.asc` and `18_Kurucz.asc`.
The plotting script only recognizes the gas codes already mapped in the code (`02`, `07`, `08`, `18`) and the sources already configured in the script (`Kurucz`, `NIST`).
If a task adds new input files or sources, update both the filename handling and the label/style mappings together.