import am4utils
from am4utils.db import init

if __name__ == "__main__":
    print(
        f"py: am4utils ({am4utils._core.__version__}), executable_path={am4utils.__path__[0]}"
    )

    init()
