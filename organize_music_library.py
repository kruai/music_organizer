import os
import re
import sys

from mutagen.id3 import ID3NoHeaderError, ID3

UNKNOWN_VALUE = "ZZZ UNKNOWN"
CHAR_REPLACEMENT_REGEX = r"[^\w\-_\.\,\&\'\+\= ]"

def setup():
    try:
        rootdir=sys.argv[1]
    except IndexError:
        print("Usage: $python organize_music_library.py {folder_path}")
        sys.exit(1)
    if os.path.exists(rootdir) and os.path.isdir(rootdir) :
        print(f"Found directory {os.path.basename(rootdir)}")
    else:
        print(f"{rootdir} directory not found. Exiting.")
        sys.exit(1)

    return rootdir


# Adds a file extension if it was stripped
def normalize_file_extension(rootdir, original_filename, extension=".mp3"):
    if original_filename.endswith(".mp3"):
        return original_filename
    else:
        new_filename = "".join([original_filename, ".mp3"])
        os.rename(
            os.path.join(rootdir, original_filename),
            os.path.join(rootdir, new_filename)
        )
        return new_filename


def get_value_from_tags(tags, search_tag_list):
    for tag in search_tag_list:
        if tag in tags:
            normalized_tag = str(tags.get(tag)).rstrip("., ")
            if len(normalized_tag) > 0:
                return str(tags.get(tag)).rstrip("., ")
    return UNKNOWN_VALUE


def main():
    rootdir = setup()

    for original_filename in os.listdir(rootdir):
        # Don't process dirs
        if os.path.isdir(os.path.join(rootdir, original_filename)):
            continue
        
        filename = normalize_file_extension(rootdir, original_filename)

        # Get the metadata tags. 
        try: 
            tags = ID3(os.path.join(rootdir, filename))
            artist = re.sub(CHAR_REPLACEMENT_REGEX, "_", get_value_from_tags(tags, ["TPE2", "TPE1", "TCOM", "TPE4", "TOPE"]))
            if len(artist.split(",")) > 2 or artist.lower().startswith("various"):
                artist = "Various Artists"
            album = re.sub(CHAR_REPLACEMENT_REGEX, "_", get_value_from_tags(tags, ["TALB", "TOAL"]))
            print(f"Got ID3 tags for {filename}")
        except ID3NoHeaderError:
            artist = UNKNOWN_VALUE
            album = UNKNOWN_VALUE
            print(f"No ID3 header found for {filename}")

        # Make directories as needed, and move the file
        os.makedirs(os.path.join(rootdir, artist, album), exist_ok=True)
        os.rename(os.path.join(rootdir, filename), os.path.join(rootdir, artist, album, filename))
        
    print("\nOrganization complete!\n")
    sys.exit(0)

if __name__ == "__main__":
    main()
