# kebab-tqdm

A [`tqdm`](https://github.com/tqdm/tqdm) progress bar — but instead of a bar,
Karim from [Karim's Kebab](https://maps.app.goo.gl/c4kMGDbDMhQZdrkB9) shaves a
turning döner spit. The cone spins (scrolling shading bands), a diagonal knife
sweeps up and down in his fist, and the shaved meat piles up in the foil tray as
your loop progresses.

## Install

```bash
pip install kebab-tqdm
```

## Usage

Drop-in replacement for `tqdm`:

```python
from kebab_tqdm import tqdm

for x in tqdm(range(100)):
    ...
```

It accepts the usual `tqdm` arguments (`desc=`, `total=`, etc.). Because the
scene is tall and redraws in place, give your loop some time per step and let it
refresh every iteration:

```python
import time
from kebab_tqdm import tqdm

for x in tqdm(range(100), desc="dinner", mininterval=0):
    time.sleep(0.05)
```

Or just run the demo:

```bash
python -m kebab_tqdm      # or: kebab-demo
```

## Notes

- Needs a **monospace** terminal that renders box/braille characters at uniform
  width (Windows Terminal, VS Code's terminal, most modern emulators). Give it
  enough width (~90 cols) and height (~53 rows) so the scene isn't wrapped.
- ANSI escape handling is enabled automatically on Windows.

## License

MIT
