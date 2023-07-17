import am4utils
from am4utils.aircraft import Aircraft
from am4utils.airport import Airport
from am4utils.route import Route

if __name__ == '__main__':
    print(f'py: am4utils ({am4utils._core.__version__}), executable_path={am4utils.__path__[0]}')
    am4utils.db.init()