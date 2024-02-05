import re
import shutil
import pybind11_stubgen
import logging

if __name__ == '__main__':
    shutil.rmtree('stubs', ignore_errors=True)
    
    pybind11_stubgen.StubsGenerator.GLOBAL_CLASSNAME_REPLACEMENTS.update({
        # re.compile(r'union (\w+)'): lambda m: m.group(1),
        # re.compile(r'PurchasedAircaftConfig'): lambda m: 'PurchasedAircraftConfig',
        # re.compile(r'::'): lambda m: '.', # scoped enum in class
    })

    pybind11_stubgen.main(
        [
            "-o", ".",
            # "--ignore-invalid", "all",
            "--no-setup-py",
            "am4utils",
        ],
    )

    shutil.move('am4utils-stubs', 'stubs')
    
    def replace(fn, map):
        with open(fn, 'r+') as f:
            contents = f.read()
            for k, v in map.items():
                contents = contents.replace(k, v)
            f.seek(0)
            f.write(contents)
            f.truncate()
    
    replace('stubs/_core/route/__init__.pyi', {
        'import am4utils._core.game': 'import am4utils._core.game\nimport am4utils._core.ticket\nimport am4utils._core.demand',
    })
    replace('stubs/_core/ticket/__init__.pyi', {
        'import am4utils._core.ticket': 'import am4utils._core.ticket\nimport am4utils._core.game',
    })

    try:
        import am4utils

        target_path = am4utils.__path__[0]
        shutil.copytree('stubs', target_path, dirs_exist_ok=True)
    except ImportError:
        print('am4utils not installed, skipping copying stubs.')