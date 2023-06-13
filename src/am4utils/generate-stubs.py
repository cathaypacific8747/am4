import re
import shutil
import pybind11_stubgen

if __name__ == '__main__':
    shutil.rmtree('stubs', ignore_errors=True)
    
    pybind11_stubgen.StubsGenerator.GLOBAL_CLASSNAME_REPLACEMENTS.update({
        re.compile(r'union (\w+)'): lambda m: m.group(1),
        re.compile(r'PurchasedAircaftConfig'): lambda m: 'PurchasedAircraftConfig',
    })

    pybind11_stubgen.main(
        [
            "am4utils",
            "-o", ".",
            "--no-setup-py",
        ],
    )
    shutil.move('am4utils-stubs', 'stubs')

    try:
        import am4utils

        target_path = am4utils.__path__[0]
        shutil.copytree('stubs', target_path, dirs_exist_ok=True)
    except ImportError:
        print('am4utils not installed, skipping copying stubs.')