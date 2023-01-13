import os


def get():
    return os.path.abspath(__file__ + "/../../..")


if __name__ == "__main__":
    print(get_abs_path())
