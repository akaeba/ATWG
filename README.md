![Python 3.7](https://img.shields.io/badge/Python-3.7-blue.svg) [![Unittest](https://github.com/akaeba/ATWG/workflows/Unittest/badge.svg)](https://github.com/akaeba/ATWG/actions)

# ATWG

__Arbitrary Temperature Waveform Generator__

A various waveform shapes creating python script to control a climate chamber via PC.


## Releases

| Version                                              | Date       | Source                                                                                   | Change log                                           |
| ---------------------------------------------------- | ---------- | ---------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| latest                                               |            | <a id="raw-url" href="https://github.com/akaeba/ATWG/archive/master.zip ">latest.zip</a> |                                                      |
| [v0.1.5](https://github.com/akaeba/ATWG/tree/v0.1.5) | 2021-07-05 | <a id="raw-url" href="https://github.com/akaeba/ATWG/archive/v0.1.5.zip ">v0.1.5.zip</a> | revised CLI interface and defaults                   |
| [v0.1.4](https://github.com/akaeba/ATWG/tree/v0.1.4) | 2021-01-17 | <a id="raw-url" href="https://github.com/akaeba/ATWG/archive/v0.1.4.zip ">v0.1.4.zip</a> | added missing files to python package                |
| [v0.1.3](https://github.com/akaeba/ATWG/tree/v0.1.3) | 2021-01-17 | <a id="raw-url" href="https://github.com/akaeba/ATWG/archive/v0.1.3.zip ">v0.1.3.zip</a> | [atwg-cli](./atwg-cli) is registered as command      |
| [v0.1.1](https://github.com/akaeba/ATWG/tree/v0.1.1) | 2021-01-02 | <a id="raw-url" href="https://github.com/akaeba/ATWG/archive/v0.1.1.zip ">v0.1.1.zip</a> | [pypi.org](https://pypi.org/project/ATWG/) published |
| [v0.1.0](https://github.com/akaeba/ATWG/tree/v0.1.0) | 2020-03-09 | <a id="raw-url" href="https://github.com/akaeba/ATWG/archive/v0.1.0.zip ">v0.1.0.zip</a> | initial draft                                        |


## Supported climate chambers
 * [Espec Corp SH-641](https://espec.com/na/products/model/sh_641)
    - RS232 communication interface
    - Espec S-2 controller


## Install

### [pip](https://pypi.org/project/ATWG/)
 * Install : `python3.7 -m pip install ATWG `
 * Update  : `python3.7 -m pip install --upgrade ATWG `

### [Github](https://github.com/akaeba/ATWG)
`git clone https://github.com/akaeba/ATWG.git `


## Command line interface

### Options

| Option           | Description                               | Args                                                                                                                |
| ---------------- | ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| --sine           | select sine as used waveform              |                                                                                                                     |
| --trapezoid      | select trapezoid as used waveform         |                                                                                                                     |
| --minTemp=myVal  | sets minimal temperature value            |                                                                                                                     |
| --maxTemp=myVal  | sets maximal temperature value            |                                                                                                                     |
| [--invert]       | start with lower part of wave             |                                                                                                                     |
| [--period=1h]    | period of waveform                        | d:hh:mm:ss, h, m, s                                                                                                 |
| [--startTemp=25] | waves start temperature                   | start temperature of wave                                                                                           |
| [--riseTime=0]   | positive slew rate, used by '--trapezoid' | degree/time, T(min->max); 5C/h, 120min                                                                              |
| [--fallTime=0]   | negative slew rate, used by '--trapezoid' | degree/time, T(max->min); 5C/h, 120min                                                                              |
| [--chamber=SIM]  | chamber type                              | [SIM](./ATWG/driver/sim/simChamber.py), [ESPEC_SH641](./ATWG/driver/espec/sh641.py)                                 |
| [--port=]        | chamber interfacing port                  | [SH641 default](./ATWG/driver/espec/sh641InterfaceDefault.yml): <br /> WinNT: `COM1 ` <br /> Linux: `/dev/ttyUSB0 ` |


### Run

#### Call

| Platform | Command                   |
|:-------- |:------------------------- |
| Windows  | python3 ./atwg-cli [ARGS] |
| Linux    | atwg-cli [ARGS]           |
| Anaconda | run ./atwg-cli [ARGS]     |

[ARGS]: `--sine --chamber=SIM --minTemp=10 --maxTemp=60 --startTemp=30 --period=1h `

This example starts the waveform generator in the simulation mode. The sine wave has a minimal value of 10°C, a
maximum of 60°C and s start value of 30°C. A full period needs one hour.


#### Output

Following output is written to the command line interface while the script is active:

```text
Arbitrary Temperature Waveform Generator

  Chamber
    State    : Run /
    Type     : SIM
    Tmeas    : +30.02 °C
    Tset     : +30.06 °C

  Waveform
    Shape    : sine
    Tmin     : +10.00 °C
    Tmax     : +60.00 °C
    Period   : 1h
    Gradient : +2.566 °C/m


Press 'CTRL + C' for exit
```


#### Permission denied error on Linux

In Linux has only the _root_ and _dialout_ group proper rights to open
_/dev/ttyUSB*_ devices. Adding the current user to the _dialout_ group
allows _ATWG_ to run without root permissions.

```bash
sudo usermod -a -G dialout $USER    # add login user to dialout group
sudo reboot                         # apply settings
```


## Chamber driver

### How-to add

The architecture of the _ATWG_ allows the fast integration of a new chamber driver. Therefore is only the import in
the [ATWG](./ATWG/ATWG.py) _open_ procedure necessary. As starting point of a new driver can the class
[simChamber](./ATWG/driver/sim/simChamber.py) serve. There are all _ATWG_ mandatory procedures as simulation
example implemented.


### Espec SH641

[sh641.py](./ATWG/driver/espec/sh641.py) realizes the interface to the climate chamber. Following instruction listing controls the chamber:

```python
from ATWG.driver.espec.sh641 import especShSu     # import driver

myChamber = especShSu()                           # call class constructor
myChamber.open()                                  # open with interface defaults
print(myChamber.get_clima())                      # get current clima
myChamber.start()                                 # start chamber
myChamber.set_clima(clima={'temperature': 25})    # set temperature value
myChamber.stop()                                  # stop chamber
myChamber.close()                                 # close handle
```

The _open_ procedure accepts as argument a .yml file with the chamber (RS232) configuration. In case of no argument [default](./ATWG/driver/espec/sh641InterfaceDefault.yml)s are used.


## References

* [Espec Corp SH-641](https://espec.com/na/products/model/sh_641)
* [Fix Serial Permission Error](https://websistent.com/fix-serial-port-permission-denied-errors-linux/)
