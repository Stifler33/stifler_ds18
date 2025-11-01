from pathlib import Path
import json
from threading import Thread
import asyncio
import time

path_1wire_devices = Path("/sys/bus/w1/devices")
__path_config = Path("config.json")
__template_config = {
    "path_devices": "/sys/bus/w1/devices",
    "devices": {"template": {
        "address": "", 
        "temp_raw": "",
        "temp_float": 0.0,
        "temp_str": ""
        }
    }
}

config = {}

def __get_config():    
    global __template_config, config
    if __path_config.is_file():        
        with open(__path_config, "r") as file:
            config = json.load(file)
            return config
    else:                        
        config = __template_config
        config["devices"].pop("template")
        with open(__path_config, "w") as file:
            json.dump(__template_config, file, indent=4)
            return __template_config
        
def __update_temps_raw(path_device: Path):    
    if path_device.is_dir():        
        with open(path_device/"temperature") as file:                                    
            new_temp = file.read()
            if new_temp == "":
                return None
            return new_temp.split()[0]
    else:
        return None

def __update_temps_float(path_device: Path):
    temp = __update_temps_raw(path_device)
    if temp:
        return float(temp) / 1000    
    return None

def __update_temps_str(path_device: Path):
    temp = __update_temps_raw(path_device)
    if temp:
        return str(float(temp) / 1000)
    return None


def __search_address(address: str):
    global config
    for name, conf in config['devices'].items():        
        if address in conf['address']:
            return True
    return False

def __loop():
    global config
    while True:
        for name, device in config['devices'].items():
            device['temp_raw'] = __update_temps_raw(
                Path(f'{config["path_devices"]}/{device["address"]}')
                )            
            device["temp_float"] = float(device["temp_raw"]) / 1000 if device["temp_raw"] else None
            device["temp_str"] = str(device["temp_float"]) if device["temp_raw"] else None        


def init_config():
    """
    Инициализируем конфигурационный файл для датчиков и присваиваем им имена
    """
    config = __get_config()
    path_devices = Path(config["path_devices"])
    if path_devices.is_dir():
        for dir in path_devices.rglob("*"):
            if dir.is_dir():
                address_device = dir.name.lstrip()
                if "master1" not in address_device and not __search_address(address_device):
                    new_name = input(f"Введите имя для датчика {address_device}: ")
                    config["devices"][new_name] = {"address": address_device,
                                                   "temp_raw": __update_temps_raw(dir),
                                                   "temp_float": __update_temps_float(dir),
                                                   "temp_str": __update_temps_str(dir)}
        with open(__path_config, "w") as file:
            json.dump(config, file, indent=4)

        Thread(target=__loop, daemon=True).start()

def list_devices() -> dict:
    """
    Метод для просмотра подключенных датчиков
    Returns:
        dict: список доступных устройств
        'name_device': Path_device
    """
    if path_1wire_devices.is_dir():        
        dict_devices = dict()
        for dir in path_1wire_devices.rglob("*"):
            if dir.is_dir():           
                if "master1" not in dir.name.lstrip():                    
                    dict_devices[dir.name.lstrip()] = dir
    return dict_devices

def get_temp(name_sensor: str):
    """
    Возвращает температуру в градусах Цельсия
    """    
    global config   
    return config['devices'][name_sensor]['temp_float']
    # path_device = Path(f"{config['path_devices']}/{config['devices'][name_sensor]["address"]}")    
    # if path_device.is_dir():        
    #     temp = __update_temps_float(path_device)        
    #     return temp