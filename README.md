# spotipy_special_tricks
Tiny Spotipy toolkit for quick, smarter Spotify playlists : custom A/B shuffles, reverse order mixes, a few extra tricks to inspect and tweak your playlists.


Small convenience scripts for managing Spotify playlists using Python and [Spotipy](https://spotipy.readthedocs.io/).

Current features:

- **Merge two playlists into a new one** by interleaving their tracks
  - Supports per-playlist limits
  - Uses a custom pattern (playlist 1 forward, playlist 2 in reverse)
- **List track titles + first artist** for a given playlist

• • •

## Requirements

- Python 3.9+
- A Spotify account
- A Spotify app (for API credentials)
- The following Python packages:
  - `spotipy`
  - `python-dotenv`

Install dependencies:

```bash
pip install spotipy python-dotenv
