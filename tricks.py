#!/usr/bin/env python3
import argparse
import datetime
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
load_dotenv()

# scopes needed for reading + creating + modifying playlists
SCOPE = "playlist-modify-private playlist-modify-public"

# global spotify client
sp = Spotify(auth_manager=SpotifyOAuth(scope=SCOPE))


def get_all_track_uris(playlist_id: str, limit: int | None = None) -> list[str]:
    """
    Fetch all track URIs from a playlist.
    If 'limit' is provided, stop after collecting that many tracks.
    """

    uris: list[str] = []
    results = sp.playlist_tracks(
        playlist_id,
        fields="items.track.uri,next",
    )

    while results and (limit is None or len(uris) < limit):
        for item in results["items"]:
            track = item.get("track")
            if track:
                uris.append(track["uri"])
                if limit is not None and len(uris) >= limit:
                    break

        if limit is not None and len(uris) >= limit:
            break

        if results.get("next"):
            results = sp.next(results)
        else:
            results = None

    return uris


def merge_playlists(
    src1_id: str,
    src2_id: str,
    new_name: str,
    per_src_limit: int = 100,
) -> None:
    """
    Merge two playlists by interleaving tracks and create a new playlist.

    Pattern:
    - Playlist 1 in normal order
    - Playlist 2 in reverse order
    - Stops when both lists are exhausted or limits are reached
    """

    user_id = sp.current_user()["id"]
    # print(f"Current user: {user_id}")

    # print(f"Fetching up to {per_src_limit} tracks from playlist 1: {src1_id}")
    tracks1 = get_all_track_uris(src1_id, limit=per_src_limit)

    # print(f"Fetching up to {per_src_limit} tracks from playlist 2: {src2_id}")
    tracks2 = get_all_track_uris(src2_id, limit=per_src_limit)

    # print(f"Playlist 1 tracks: {len(tracks1)}")
    # print(f"Playlist 2 tracks: {len(tracks2)}")

    merged: list[str] = []
    max_len = max(len(tracks1), len(tracks2))

    for i in range(max_len):
        if i < len(tracks1):
            merged.append(tracks1[i])
        if i < len(tracks2):
            #take from playlist 2 in reverse order
            # j = len(tracks2) - i - 1
            merged.append(tracks2[i])

    # print(f"Total merged tracks: {len(merged)}")

    # create new playlist (private by default)
    # print(f"Creating new playlist: {new_name}")
    new_pl = sp.user_playlist_create(user_id, new_name, public=False)

    # --Spotify allows adding up to 100 tracks per request
    for i in range(0, len(merged), 100):
        batch = merged[i : i + 100]
        sp.playlist_add_items(new_pl["id"], batch)
        # print(f"added tracks {i}–{i + len(batch) - 1}")

    print(f"created playlist '{new_name}' with {len(merged)} tracks.")
    # print(f"Playlist ID: {new_pl['id']}")


def print_titles(playlist_id: str) -> None:
    results = sp.playlist_tracks(
        playlist_id,
        fields="items(track(name, artists(name))),next",
    )

    while results:
        for item in results["items"]:
            track = item.get("track")
            if not track:
                continue

            name = track["name"]
            artists = track.get("artists") or []
            if artists:
                artist_name = artists[0]["name"]

            print(f"{name} - {artist_name}")

        if results.get("next"):
            results = sp.next(results)
        else:
            break


def build_parser() -> argparse.ArgumentParser:
    """
    Build the top-level CLI argument parser.
    """
    parser = argparse.ArgumentParser(
        description="Small convenience tools for managing Spotify playlists."
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # merge command
    merge_parser = subparsers.add_parser(
        "merge",
        help="Merge two playlists into a new one with an interleaving pattern.",
    )
    merge_parser.add_argument(
        "--src1",
        required=True,
        help="Source playlist 1 ID",
    )
    merge_parser.add_argument(
        "--src2",
        required=True,
        help="Source playlist 2 ID",
    )
    merge_parser.add_argument(
        "--name",
        required=False,
        help="Name of the new playlist. If omitted, a default based on the current month is used.",
    )
    merge_parser.add_argument(
        "--per-src-limit",
        type=int,
        default=100,
        help="Max number of tracks to take from each source playlist (default: 100).",
    )

    # titles command
    titles_parser = subparsers.add_parser(
        "titles",
        help="Print track titles and first artist for a playlist.",
    )
    titles_parser.add_argument(
        "--playlist",
        required=True,
        help="Playlist ID to print titles from.",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "merge":
        new_name = (
            args.name
            if args.name
            else f"Mixed playlist {datetime.datetime.now().strftime('%Y-%m-%d')}"
        )
        merge_playlists(
            src1_id=args.src1,
            src2_id=args.src2,
            new_name=new_name,
            per_src_limit=args.per_src_limit,
        )

    elif args.command == "titles":
        print_titles(args.playlist)


if __name__ == "__main__":
    main()
