import os



def create_file_dict(root_dir: str) -> dict[str, list[str]]:
    file_dict = {}

    # List all items in root_dir
    for item in os.listdir(root_dir):
        # Construct the full path to the item
        full_path = os.path.join(root_dir, item)

        # If the item is a directory, list all files in it
        if os.path.isdir(full_path):
            file_dict[item] = os.listdir(full_path)

    return file_dict
