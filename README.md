# AdaRF
Datasets and code used in AdaRF.

## Dataset
There are 5 datasets and each one contains a training data and test data. 

### Setup
Some descriptions can be found at Table. 2 in the original paper. The detailed experimental settings are described in 'config.txt', where each line represents the config of an experiment. And each line is a string formatted of "A I:X Y P F S".
* A: date. e.g. "1118" indicates 18 November 2018 while "0114" indicates 14 January 2019.
* I: start index and end index (included). e.g. "1-5" represents 5 experiments from "01" to "05".
* X: the center x-coordinate of the tag sequence with the unit of cm.
* Y: the y-coordinate of the tag sequence with the unit of cm.
* P: the number of aperture points (measurement points). DEFAULT: 50.
* F: the number of frequency (channel). DEFAULT: 8 or 1.
* S: the separation between adjacent tags with the unit of cm. It is an optional item.

In the training data or test data, each folder represent a experiment. There are 50 CSV files in an experiment and each file represent the signal profile collected at an aperture point. In the each CSV file, it consists of the following information:
* EPC: the unique ID of an RFID tag. 24 digits.
* antennaindex: the index of antenna. DEFAULT: 1.
* frequency: the frequency of each item. Range from 920.625 MHz to 924.125 MHz with a step of 0.5 MHz.
* time: INVALID.
* RSSI: a negative real number.
* phase: a real number ranging from 0 to 2pi.
* dopplershift: the dopplershift reported by Impinj reader, which might be inaccurate indicator and is not used in our system.
* velocity: INVALID.
* x: the x-coordinate of the aperture point with the unit of m.
* y: the y-coordinate of the aperture point with the unit of m. DEFAULT: 0. "1.63" is INVALID.
* z: the z-coordinate of the aperture point with the unit of m. DEFAULT: 0.
* angle: INVALID.

A, I, P and S comprose forms a mapping between the config and folder. For instance, config "1118 1-5:50 45 50 8" maps to the folders from "181118-01-50-8" to "181118-05-50-8".

### Reconstruct tag location
In each experiment, antenna scans several RFID tags. All tags have the same y-coordinate and the separation between adjacent tags are also same. Therefore, we can reconstruct their locations according to X, Y, S and the number of tags. For instance, if X=50 Y=45 S=20 and the number of tags is 3, the coordinates of these tags are (30, 45), (50, 45) and (70, 45). Note that we only consider locate RFID tag in 2D plane since we only adopt one antenna.

The corresponding function is available the Python file named 'config.py'.

### Extract signal profile (update soon)

## Code  (update soon)

