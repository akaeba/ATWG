# ATWG
__Arbitrary Temperature Waveform Generator__

A various waveform shapes creating python script to control a climate chamber via PC.


## Requirements

### Python
 * Python 3.x

### Supported climate chambers
 * [Espec Corp SH-641](https://espec.com/na/products/model/sh_641)

### Communication interface
 * RS232


## Command line interface (CLI)

### Arguments
tbd.

### Waveforms

#### Sine

The python command line call forces the climate chamber to perform an sine function with minimal 10°C and maximal 30°C. A full sine period needs one hour.

```python
run ./src/ATWG.py --wave=sine --chamber=ESPEC_SH641 --tmin=10 --tmax=30 --period=1h
```


## Chamber driver only

### Espec SH641
[sh_641_drv.py](https://github.com/akaeba/ATWG/blob/master/espec/sh_641_drv.py) realizes the interface to the climate chamber. For control is the following instruction set to use.

```python
import espec.sh_641_drv as sh_641_drv   # import driver

myChamber = especShSu()                 # create instance
myChamber.open()                        # open RS232 interface with defaults
myChamber.start()                       # chamber starts with operation
myChamber.set_temperature(25)           # set target temperature
myChamber.stop()                        # stop chamber
```

The _open_ procedure accepts as argument an yaml file with RS232 configuration. In case of no argument is the [default](https://github.com/akaeba/ATWG/blob/master/espec/sh_if_default.yaml) used.


## File listing

| Name | Path | Remark |
| ---- | ---- | ------ |
