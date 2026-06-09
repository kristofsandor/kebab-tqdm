"""Demo: ``python -m kebab_tqdm`` (or the ``kebab-demo`` console script)."""
import time

from . import tqdm


def main():
    for _ in tqdm(range(100), desc="dinner", mininterval=0):
        time.sleep(0.05)


if __name__ == "__main__":
    main()
