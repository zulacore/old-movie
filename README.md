# old-movie

Ever wanted to generate a video that looks like an old movie, with that "TO BE CONTINUED..." title card and all the classic grain, shake, and dust? That's exactly what this is about.

This project was born once because I needed exactly that: overlaying text on a video with an old-film aesthetic. It worked, and it's kept here purely for fun and curiosity.

**Honest warning:** it's not meant to be maintained, nor will it receive ongoing care. Treat it as a fun experiment that does what it's supposed to do. If it's useful to you, great; if you want something serious, you probably want to look elsewhere.

## Requirements

- Python >= 3.14
- [uv](https://docs.astral.sh/uv/) (dependency manager)
- Alternative: Nix environment with `nix develop` (see `flake.nix`)

## Installation

With `uv`:

```bash
uv sync
```

## Usage

With `uv`:

```bash
uv run old-movie
```

With Nix (`nix develop`), `uv` is not available in the environment; run it directly with the nixpkgs Python:

```bash
nix develop
python -m old_movie
```

> Whether you use `uv` or Nix, the behavior is the same: both paths reproduce the same result. Pick whichever you prefer.

### Options

```bash
uv run old-movie "END OF CHAPTER" --seconds 6 --shake 1.5 --fps 30 -o output.mp4
```

Main flags:

| Flag          | Default             | Description                    |
| ------------- | ------------------- | ------------------------------ |
| `text`        | `TO BE CONTINUED...`| Title card text (positional)   |
| `-o/--output` | `old_title.mp4`    | Output file                    |
| `--seconds`   | `4.0`               | Duration in seconds            |
| `--fps`       | `24`                | Frames per second              |
| `--width`     | `1280`              | Width                          |
| `--height`    | `720`               | Height                         |
| `--font-size` | `92`                | Font size                      |
| `--font`      | (auto)              | Path to a TTF/OTF font         |
| `--shake`     | `1.0`               | Shake intensity                |
| `--seed`      | `7`                 | Random seed                    |

See all options: `uv run old-movie --help`.

## Development

Development environment via Nix (Python + Pillow pinned only via nixpkgs):

```bash
nix develop
```
