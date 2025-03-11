import yaml
import os

class Config:
    def __init__(self, config_file='config.yaml', config_folder='PortDrayageData'):
        config_path = os.path.join(config_folder, config_file)
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)

    def get(self, key, default=None):
        return self.config.get(key, default)

if __name__ == "__main__":
    config = Config()
    vehicles = config.get('vehicles')
    cargos = config.get('cargos')
    print([vehicle['id'] for vehicle in vehicles])
    print([cargo['name'] for cargo in cargos])
