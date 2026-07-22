from math import floor


def get_album_image(album, size_priority):
    images = {image["size"]: image["#text"] for image in album["image"]}
    image = None
    if "image" in album and len(images) > 0:
        for prio in size_priority:
            if prio in images:
                image = images[prio]
                break
        if image is None or image == "":
            image = next(iter(images.values()))
    if image == "":
        image = None
    return image


PADDING_H = 60
PADDING_W = 60
GAP_SIZE = 7


def calc_album_count(w, h, col):
    single_size = (w / col) + GAP_SIZE
    rows = floor(h / single_size)

    v = rows * col
    return floor(v)


def run(input):
    width = input["trmnl"]["device"]["width"]
    height = input["trmnl"]["device"]["height"]
    if width <= 600:  # sm
        # priorities for album cover sizes depending on device size
        size_priority = ["medium", "large", "extralarge"]
        # grid size is the base grid size for this size class & layout
        # first elem is num columns, second num rows
        num_cols = {"full": 2, "half": 2, "half-vert": 2, "quad": 2}
    elif width <= 800:  # md
        size_priority = ["large", "extralarge", "medium"]
        num_cols = {"full": 4, "half": 5, "half-vert": 2, "quad": 2}
    else:  # lg
        size_priority = ["extralarge", "large", "medium"]
        num_cols = {"full": 5, "half": 4, "half-vert": 3, "quad": 2}

    max_albums = {
        "full": calc_album_count(width - PADDING_W, height - PADDING_H, num_cols["full"]),
        "half": calc_album_count(width - PADDING_W, height / 2 - PADDING_H, num_cols["half"]),
        "half-vert": calc_album_count(width / 2 - PADDING_W, height - PADDING_H, num_cols["half-vert"]),
        "quad": calc_album_count(width / 2 - PADDING_W, height / 2 - PADDING_H, num_cols["quad"]),
    }
    abs_max_albums = max(max_albums.values())

    albums = []
    if "topalbums" in input and "album" in input["topalbums"]:
        for album in input["topalbums"]["album"]:
            image = get_album_image(album, size_priority)
            if image is not None:
                albums.append({
                    "name": album["name"],
                    "artist": album["artist"]["name"] if "artist" in album else "",
                    "image": image,
                })
            if len(albums) >= abs_max_albums:
                break
    elif "recenttracks" in input and "track" in input["recenttracks"]:
        already_collected_albums = set()
        for track in input["recenttracks"]["track"]:
            if "album" in track:
                album_name = track["album"]["#text"]
                artist_name = track["artist"]["#text"] if "artist" in track else ""
                needle = (artist_name, album_name)
                if needle not in already_collected_albums:
                    image = get_album_image(track, size_priority)
                    already_collected_albums.add(needle)
                    albums.append({
                        "name": album_name,
                        "artist": artist_name,
                        "image": image,
                    })
                    if len(albums) >= abs_max_albums:
                        break

    if len(albums) < 1:
        return {"errors": ["Last.fm API did not return any albums"]}

    return {"data": {"albums": albums}, "num_cols": num_cols, "max_albums": max_albums}
