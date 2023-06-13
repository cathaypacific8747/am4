import am4utils

if __name__ == '__main__':
    print(f'py: am4utils ({am4utils._core.__version__}), executable_path={am4utils.__path__[0]}')
    am4utils.db.init(am4utils.__path__[0])

    a0 = am4utils.aircraft.Aircraft.from_auto('name:B747-400')
    assert a0.shortname == "b744"
    help(a0.type)