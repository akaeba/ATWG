# ATWG

![Python 3.7](https://img.shields.io/badge/Python-3.7-blue.svg) [![Unittest](https://github.com/akaeba/ATWG/workflows/Unittest/badge.svg)](https://github.com/akaeba/ATWG/actions)

__Arbitrary Temperature Waveform Generator__

A various waveform shapes creating python script to control a climate chamber via PC.


## Requirements

### Supported climate chambers
 * [Espec Corp SH-641](https://espec.com/na/products/model/sh_641)
    - RS232 communication interface
    - Espec S-2 controller


## Temperature Waveform generator

### CLI

#### Arguments
tbd.

#### Waveforms

##### Sine

The python command line call forces the climate chamber to perform an sine function with minimal 10°C and maximal 30°C. A full sine period needs one hour.

```python
run ./src/ATWG.py --wave=sine --chamber=ESPEC_SH641 --tmin=10 --tmax=30 --period=1h
```


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

The _open_ procedure accepts as argument a .yaml file with the chamber (RS232) configuration. In case of no argument [default](https://github.com/akaeba/ATWG/blob/master/espec/sh_if_default.yaml)s are used.


## File listing

| Name | Path | Remark |
| ---- | ---- | ------ |
