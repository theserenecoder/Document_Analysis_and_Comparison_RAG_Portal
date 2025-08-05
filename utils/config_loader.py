import yaml

def load_config(config_path: str = "config\config.yaml") ->dict:
    '''This function will load the config file (config.yaml)'''
    
    with open(config_path,'r') as file:
        config = yaml.safe_load(file)
    return config


if __name__=='__main__':
    print(load_config())