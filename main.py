import datetime
import json
import os
import pickle
import shutil
import time

WATCH_DIR = "/watch"
TRASH_DIR = "/trash"


def formated_time():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def auto_log(msg, file="data/auto-clean.log", max_lines=10000):
    msg_str = f"[{formated_time()}] {msg}"
    print(msg_str)
    with open(file, "a") as f:
        f.write(msg_str + '\n')
    if os.path.isfile(file):
        with open(file, "r") as f:
            lines = f.readlines()
        if lines and len(lines) > max_lines:
            with open(file, "w") as f:
                f.writelines(lines[-max_lines:])


def main():
    # Move default-config.json to data/config.json if not exist
    if not os.path.isfile("data/config.json"):
        shutil.copy("default-config.json", "data/config.json")

    # Load config
    with open("data/config.json", "r") as f:
        config = json.load(f)
        max_keep_days = config["max_keep_days"]
        move_to_trash = config["move_to_trash"]
        exclude = config["exclude"]

    # Get current files
    current_files = {}
    for file in os.listdir(WATCH_DIR):
        if file in exclude:
            continue
        inode = os.stat(f"{WATCH_DIR}/{file}").st_ino
        is_dir = os.path.isdir(f"{WATCH_DIR}/{file}")
        current_files[inode] = {"name": file, "is_dir": is_dir}

    # Load cache from file
    cache_file = "data/cache.pkl"
    if os.path.isfile(cache_file):
        with open(cache_file, "rb") as f:
            cache = pickle.load(f)
    else:
        cache = {}

    # Update cache with inode with new name
    for inode, detail in current_files.items():
        if inode in cache:
            if cache[inode]["name"] != detail["name"]:
                # log.append(
                auto_log(f"File name changed: \"{cache[inode]['name']}\" -> \"{detail['name']}\"")
                cache[inode]["name"] = detail["name"]
            if cache[inode]["is_dir"] != detail["is_dir"]:
                auto_log(f"File type changed: \"{cache[inode]['name']}\"")
                cache[inode]["is_dir"] = detail["is_dir"]

    # Remove files in cache that are not in current_files
    for inode in cache.copy():
        if inode not in current_files:
            auto_log(f"File already removed: \"{cache[inode]['name']}\"")
            del cache[inode]

    # Add new files in current_files to cache
    for inode in current_files:
        if inode not in cache:
            cache[inode] = {
                'name': current_files[inode]['name'],
                'is_dir': current_files[inode]['is_dir'],
                'add_time': datetime.datetime.now()
            }
            auto_log(f"New file added: \"{cache[inode]['name']}\"")

    # Delete files in cache that are too old
    for inode in cache.copy():
        if (datetime.datetime.now() - cache[inode]['add_time']).days > max_keep_days:
            if move_to_trash:
                shutil.move(f"{WATCH_DIR}/{cache[inode]['name']}", TRASH_DIR)
                auto_log(f"Moved to trash: \"{cache[inode]['name']}\"")
            else:
                if cache[inode]['is_dir']:
                    shutil.rmtree(f"{WATCH_DIR}/{cache[inode]['name']}")
                else:
                    os.remove(f"{WATCH_DIR}/{cache[inode]['name']}")
                auto_log(f"Deleted: \"{cache[inode]['name']}\"")
            del cache[inode]

    # Save cache to file
    with open(cache_file, "wb") as f:
        pickle.dump(cache, f)


if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as e:
            auto_log(f"Error: {e}")

        time.sleep(3600)
