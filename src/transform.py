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


def run(input):
    width = input["trmnl"]["device"]["width"]
    if width <= 600:  # sm
        # priorities for album cover sizes depending on device size
        size_priority = ["medium", "large", "extralarge"]
        # max album count to send to frontend
        max_albums = 4
        # grid size is the base grid size for this size class & layout
        # first elem is num columns, second num rows
        num_cols = {"full": 2, "half": 2, "half-vert": 2, "quad": 2}
    elif width <= 800:  # md
        size_priority = ["large", "extralarge", "medium"]
        max_albums = 8
        num_cols = {"full": 4, "half": 5, "half-vert": 2, "quad": 2}
    else:  # lg
        size_priority = ["extralarge", "large", "medium"]
        max_albums = 15
        num_cols = {"full": 5, "half": 4, "half-vert": 3, "quad": 2}

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

    if len(albums) < 1:
        return {"errors": ["Last.fm API did not return any albums"]}

    return {"data": {"albums": albums[:max_albums]}, "num_cols": num_cols}
