![Python 3.7](https://img.shields.io/badge/Python-3.7-blue.svg) [![Unittest](https://github.com/akaeba/ATWG/workflows/Unittest/badge.svg)](https://github.com/akaeba/ATWG/actions)

# ATWG

__Arbitrary Temperature Waveform Generator__

A various waveform shapes creating python script to control a climate chamber via PC.


## Releases


## Command line interface

### Options


| Option           | Description                               | Args                                                                                 |
| ---------------- | ------------------------------------------| ------------------------------------------------------------------------------------ |
| --sine           | select sine as used waveform              |                                                                                      |
| --trapezoid      | select trapezoid as used waveform         |                                                                                      |
| --minTemp=myVal  | sets minimal temperature value            |                                                                                      |
| --maxTemp=myVal  | sets maximal temperature value            |                                                                                      |
| [--invert]       | start with lower part of wave             |                                                                                      |
| [--period=1h]    | period of waveform                        | d:hh:mm:ss, h, m, s                                                                  |
| [--startTemp=25] | waves start temperature                   | start temperature of wave                                                            |
| [--riseTime=0]   | positive slew rate, used by '--trapezoid' | degree/time, T(min->max); 5C/h, 120min                                               |
| [--fallTime=0]   | negative slew rate, used by '--trapezoid' | degree/time, T(min->max); 5C/h, 120min                                               |
| [--chamber=SIM]  | used chamber                              | SIM, ESPEC_SH641                                                                     |
| [--itfCfgFile=]  | chambers interface configuration          | [default](https://github.com/akaeba/ATWG/blob/master/driver/espec/sh_if_default.yml) |


### Example

This example starts the waveform generator in the simulation mode. As wave is a sine with a minimal temperature of 10°C and maximal 60°C. A full
sine period needs one hour. The start temperature is set to 30°C.

```python
run ./ATWG.py --sine --chamber=SIM --minTemp=10 --maxTemp=60 --startTemp=30 --period=1h
```


### Output

Following output is written to the command line interface while the script is active:

```bash
Arbitrary Temperature Waveform Generator

  Chamber
    State    : Run |
    Tmeas    : +30.06 °C
    Tset     : +30.10 °C

  Waveform
    Shape    : sine
    Tmin     : +10.00 °C
    Tmax     : +60.00 °C
    Period   : 1h
    Gradient : +0.043 °C/sec


Press 'CTRL + C' for exit
```


## Supported climate chambers
 * [Espec Corp SH-641](https://espec.com/na/products/model/sh_641)
    - RS232 communication interface
    - Espec S-2 controller


## Chamber driver only

### Espec SH641
[sh_641_drv.py](https://github.com/akaeba/ATWG/blob/master/espec/sh_641_drv.py) realizes the interface to the climate chamber. Following instruction listing controls the chamber:

```python
import espec.sh_641_drv as sh_641_drv   # import driver

myChamber = especShSu()                 # create instance
myChamber.open()                        # open RS232 interface with defaults
myChamber.start()                       # chamber starts with operation
myChamber.set_temperature(25)           # set target temperature
myChamber.stop()                        # stop chamber
```

The _open_ procedure accepts as argument a .yml file with the chamber (RS232) configuration. In case of no argument [default](https://github.com/akaeba/ATWG/blob/master/driver/espec/sh_if_default.yml)s are used.


## File listing

| Name | Path | Remark |
| ---- | ---- | ------ |
