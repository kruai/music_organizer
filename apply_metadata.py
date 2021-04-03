import csv
import os
import re
import sys

from mutagen.id3 import ID3NoHeaderError, ID3, TIT2, TALB, TPE1, TPE2
from organize_music_library import normalize_file_extension

UNKNOWN_VALUE = "ZZZ UNKNOWN"
STRIP_CHARS = r"(\.mp3)|(\([0-9]+\))|[^a-zA-Z0-9]"

def setup():
    try:
        rootdir=sys.argv[1]
        metadata_file=sys.argv[2]
    except IndexError:
        print("Usage: $python apply_metadata.py {folder_path} {metadata_file}")
        sys.exit(1)
    if os.path.exists(rootdir) and os.path.isdir(rootdir):
        print(f"Found directory {os.path.basename(rootdir)}")
    else:
        print(f"{rootdir} directory not found. Exiting.")
        sys.exit(1)
    if os.path.exists(metadata_file) and not os.path.isdir(metadata_file):
        print(f"Found metadata file {os.path.basename(metadata_file)}")
    else:
        print(f"{metadata_file} file not found. Exiting.")
        sys.exit(1)

    return rootdir, metadata_file


def normalize_name(name):
    return re.sub(STRIP_CHARS, '', re.sub(".mp3", "", name)[:45])


def main():
    rootdir, metadata_file = setup()
    meta_dict = dict()
    failures = 0

    with open(metadata_file, newline="", encoding="utf-8") as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=",")
        for row in csv_reader:
            meta_dict[normalize_name(row[0])] = row.copy()
            # print(normalize_name(row[0]))
        
    for original_filename in os.listdir(rootdir):
        # Don't process dirs
        if os.path.isdir(os.path.join(rootdir, original_filename)):
            continue
        
        filename = normalize_file_extension(rootdir, original_filename)
        try:
            track_metadata = meta_dict[normalize_name(filename)]
        except KeyError:
            print(f"Failed for {normalize_name(filename)}!")
            failures += 1
        
        # Read the ID3 tag or create one if not present
        try: 
            tags = ID3(os.path.join(rootdir, filename))
        except ID3NoHeaderError:
            tags = ID3()
    
        tags["TIT2"] = TIT2(encoding=3, text=track_metadata[0])
        tags["TALB"] = TALB(encoding=3, text=track_metadata[1])
        tags["TPE1"] = TPE1(encoding=3, text=track_metadata[2])
        tags["TPE2"] = TPE2(encoding=3, text=track_metadata[2])

        tags.save(os.path.join(rootdir,filename))
        
    print("\nMetadata applied!\n")
    sys.exit(0)

if __name__ == "__main__":
    main()
