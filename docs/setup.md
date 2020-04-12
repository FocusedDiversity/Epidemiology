Setting up this repository is fairly simple. The following lines of shell commands will setup a python virtual environment and install the package with all its dependencies.  
```bash
cd [repository_folder]
pip install virtualenv
virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the following command in the terminal to test successful setup of the repo:
```bash
python epidem/datamart/csse_covid19.py
```

You may run a jupyter notebook server within this python virtual environment as follows:
```bash
cd jupyter_nb/
jupyter notebook
```
Try running the 'Data Sanity Check and Basic Analysis' notebook to test the jupyter notebook server.

 
[Next: Configuration](./config.md)\
[Back to main index](../README.md) 