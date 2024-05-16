# daq_connectivity
Explore various methods for interfacing with a Data Acquisition (DAQ) system, including USB and Ethernet connections

# draft notes
pip install cannot be done directly on the rpi, we need to create a virtual env (note that sudo pip install or sudo python file.py cannot be used in venv):
```
python3 -m venv ~/daq_env  # only the first time
source ~/daq_env/bin/activate
deactivate   # only to exit venv
```

I had to do this cmd in order to pip install numpy and pandas:
```
sudo apt-get install libopenblas-dev
```

In order to push and pull from one of my repos via ssh in my rpi I had to create a fine grained token and do this:

```
git clone https://opticsensors:<MYTOKEN>@github.com/opticsensors/daq_connectivity.git 

git remote set-url origin https://scuzzlebuzzle:<MYTOKEN>@github.com/opticsensors/daq_connectivity.git

```
