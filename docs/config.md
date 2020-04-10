All configuration variables should be included in config files in the [config folder](../epidemiology/config). There are three config files for three environments namely:
1. Production: `config/prod.py`
1. Staging: `config/stage.py`
1. Development: `config/dev.py`

While including any new configuration elements ensure they are included in config files for all environments. The configuration for the environment you are running must be included in your setup by creating a symlink named `env_config.py` with the corresponding environment config file as the target in the `config` folder as follows:

```bash
$ cd [repository_folder]/epidemiology/config
$ ln -s env_config.py [environment].py 
```   

The code will included the configuration options using the `env_config.py` symlink. The setup script will create this symlink with the dev config as the target by default.

[Next: Setup](./setup.md) \
[Back to main index](../README.md) 
