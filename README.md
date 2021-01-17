![Python 3.7](https://img.shields.io/badge/Python-3.7-blue.svg) [![Unittest](https://github.com/akaeba/ATWG/workflows/Unittest/badge.svg)](https://github.com/akaeba/ATWG/actions)

# ATWG

__Arbitrary Temperature Waveform Generator__

A various waveform shapes creating python script to control a climate chamber via PC.


## Releases

| Version                                              | Date       | Source                                                                                   | Change log                                                                               |
| ---------------------------------------------------- | ---------- | ---------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| latest                                               |            | <a id="raw-url" href="https://github.com/akaeba/ATWG/archive/master.zip ">latest.zip</a> |                                                                                          |
| [v0.1.3](https://github.com/akaeba/ATWG/tree/v0.1.3) | 2021-17-01 | <a id="raw-url" href="https://github.com/akaeba/ATWG/archive/v0.1.3.zip ">v0.1.3.zip</a> | [atwg-cli](https://github.com/akaeba/ATWG/blob/master/atwg-cli) is registered as command |
| [v0.1.1](https://github.com/akaeba/ATWG/tree/v0.1.1) | 2021-02-01 | <a id="raw-url" href="https://github.com/akaeba/ATWG/archive/v0.1.1.zip ">v0.1.1.zip</a> | [pypi.org](https://pypi.org/project/ATWG/) published                                     |
| [v0.1.0](https://github.com/akaeba/ATWG/tree/v0.1.0) | 2020-03-09 | <a id="raw-url" href="https://github.com/akaeba/ATWG/archive/v0.1.0.zip ">v0.1.0.zip</a> | initial draft                                                                            |


## Supported climate chambers
 * [Espec Corp SH-641](https://espec.com/na/products/model/sh_641)
    - RS232 communication interface
    - Espec S-2 controller


## Install

### pip
 * Install : `python3.7 -m pip install ATWG `
 * Update  : `python3.7 -m pip install --upgrade ATWG `

### Github
`git clone https://github.com/akaeba/ATWG.git `


## Command line interface

### Options

| Option           | Description                               | Args                                                                                              |
| ---------------- | ----------------------------------------- | ------------------------------------------------------------------------------------------------- |
| --sine           | select sine as used waveform              |                                                                                                   |
| --trapezoid      | select trapezoid as used waveform         |                                                                                                   |
| --minTemp=myVal  | sets minimal temperature value            |                                                                                                   |
| --maxTemp=myVal  | sets maximal temperature value            |                                                                                                   |
| [--invert]       | start with lower part of wave             |                                                                                                   |
| [--period=1h]    | period of waveform                        | d:hh:mm:ss, h, m, s                                                                               |
| [--startTemp=25] | waves start temperature                   | start temperature of wave                                                                         |
| [--riseTime=0]   | positive slew rate, used by '--trapezoid' | degree/time, T(min->max); 5C/h, 120min                                                            |
| [--fallTime=0]   | negative slew rate, used by '--trapezoid' | degree/time, T(max->min); 5C/h, 120min                                                            |
| [--chamber=SIM]  | used chamber                              | SIM, ESPEC_SH641                                                                                  |
| [--itfCfgFile=]  | chambers interface configuration          | [default](https://github.com/akaeba/ATWG/blob/master/ATWG/driver/espec/sh641InterfaceDefault.yml) |


### Example

This example starts the waveform generator in the simulation mode. The sine wave has a minimal value of 10°C, a
maximum of 60°C and s start value of 30°C. A full period needs one hour.

#### Windows
`python3 ./atwg-cli --sine --chamber=SIM --minTemp=10 --maxTemp=60 --startTemp=30 --period=1min `

#### Linux
`. atwg-cli --sine --chamber=SIM --minTemp=10 --maxTemp=60 --startTemp=30 --period=1min `

#### Python Anaconda
`run ./atwg-cli --sine --chamber=SIM --minTemp=10 --maxTemp=60 --startTemp=30 --period=1min `


### Output

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
    Gradient : +2.57 °C/m


Press 'CTRL + C' for exit
```


## Chamber driver only

### Espec SH641
[sh641.py](https://github.com/akaeba/ATWG/blob/master/ATWG/driver/espec/sh641.py) realizes the interface to the climate chamber. Following instruction listing controls the chamber:

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

The _open_ procedure accepts as argument a .yml file with the chamber (RS232) configuration. In case of no argument [default](https://github.com/akaeba/ATWG/blob/master/ATWG/driver/espec/sh641InterfaceDefault.yml)s are used.
