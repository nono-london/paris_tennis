from pathlib import Path
from typing import List


def get_tennis_names() -> List:
    tennis_names: List = ['ELISABETH', 'ATLANTIQUE']
    return tennis_names


def get_project_root_path() -> Path:
    # https://stackoverflow.com/questions/5137497/find-the-current-directory-and-files-directory
    root_dir = Path(__file__).resolve().parent.parent
    return root_dir


def get_project_download_path() -> Path:
    # https://stackoverflow.com/questions/25389095/python-get-path-of-root-project-structure/40227116
    root_path: Path = get_project_root_path()
    download_folder_path = Path(root_path, root_path.name, "downloads")
    if not download_folder_path.exists():
        download_folder_path.mkdir(parents=True)
    return download_folder_path


if __name__ == '__main__':
    print(get_tennis_names())
    print(get_project_root_path())
    print(get_project_download_path())

