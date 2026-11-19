# news-image-20261119

[![bounty](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/code-ware647/mkf-news-83349/rank.svg)](https://make.fun/bounty/news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/code-ware647/mkf-news-83349/reward.svg)](https://make.fun/bounty/news-image-20261119)

A make.fun competition entry: a program that renders a 1024x768
newspaper-style front page PNG summarising world news for
**Thursday 19 November 2026**.

## Run

```bash
python3 main.py            # writes ./out/entry.png
# or
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Requires Python 3.13 (works on 3.11+), **standard library only**
(`zlib`, `struct`, `os`) — no network, no external fonor images.

## Output

`entry.png` — a front page with a masthead ("WORLD NEWS — THURSDAY
19 NOVEMBER 2026") and five headline boxes covering real evenof
19 November 2026: the GTA VI console launch day, global markets,
the COP31 climate summit, tech/AI chip news, and sport.

All text is drawn with a hand-defined 5x7 bitmap font scaled up in
code. Output is fully deterministic: running twice produces
byte-identical PNGs.

## License

MIT — see [LICENSE](LICENSE).
