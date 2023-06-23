# Latencyplot
Define a JSON file format for data exchange and provide example scripts how to create such files and generate a graph from them.

* [Purpose](#purpose)
* [Data format](#data-format)
* [Python scripts](#python-scripts)
* [Examples](#examples)

## Purpose
Create a basis for sharing data of Linux PREEMPT_RT real-time systems

## Data format
```json
{
    "format": {
        "name": "RT Dataset",
        "version": "1.0"
    },
    "timestamps": {
        "origin": <ISO creation date of data>,
        "dataset": <ISO creation date of this file>
    },
    "system": {
        "hostname": <Name of the host undergoing the latency test>
    },
    "processor": {
        "family": <Processor family>,
        "vendor": <Processor vendor>,
        "type": <Processor type>
    },
    "kernel": {
        "version": <Kernel version>,
        "patches": [
            <Array of lines of patch names>
        ],
        "config": [
            <Array of subsequent non-emtpy non-comment lines of the kernel configuration>
        ],
        "cmdline": <Kernel command line>
    },
    "condition": {
        "load": <System load conditions: "idle", "moderate", "heaavy" or "brute-force">,
        "cycles": <Total number of cyclictest cycles>,
        "interval": <Cyclictest interval in µs>,
        "cyclictest": <Cyclictest command line>
    },
    "latency": {
        "granularity": <Width of class of latency data>,
        "maxima": [
            <Array of maximum latency per core>
        ],
        "cores": [
            [
                <Two-dimensional array of number of samples per latency classes per core>
            ]
        ]
    }
}
```

## Python scripts
Two scripts are provided, one to generate a JSON data file and one to generate a latency plot from the data file. While the [first script mk-rtdataset.py](https://github.com/osadl/Latencyplot/blob/main/src/mk-rtdataset.py) is very specific and based on the particular measurement conditions of a typical OSADL QA Farm system, the [second script plot-rtdataset.py](https://github.com/osadl/Latencyplot/blob/main/src/plot-rtdataset.py) can be of general use.

## Examples
The below latency plot was generated from the [example JSON data](https://github.com/osadl/Latencyplot/blob/main/examples/r0s8.json) that are part of this repository. The two commands
```bash
mk-rtdataset.py r0s8.json
plot-rtdataset.py r0s8.json r0s8.svg
```

were executed. It should be noted that in this example the latency values have exceeded the histogram range, so that it is not sufficient to determine the maximum from the histogram itself. For such cases, the maximum latency values per core must rather be stored separately (as in the OSADL QA farm raw data) or the line beginning with "# Max Latencies:" must be evaluated additionally.
<img src="/examples/r0s8.svg" alt="Example latency plot of QA Farm system rack0slot8.osadl.org">

If an SVG suffixed output file is given and the resulting graph is displayed in a [browser](https://www.osadl.org/monitoring/latencyplots-static/r0s8.svg), per-core histograms may individually be switched on and off:
* Click on a legend element: The histogram of the related core is toggled.
* Ctrl-click on a legend element: All other histograms except the one of the clicked core are disabled.
* Shift-click on a legend element: All histograms are restored.

And here are some more examples from OSADL QA Farm systems:
<img src="/examples/r0s0.svg" alt="Example latency plot of QA Farm system rack0slot0.osadl.org">
<img src="/examples/r3s5.svg" alt="Example latency plot of QA Farm system rack3slot5.osadl.org">
<img src="/examples/r6s8.svg" alt="Example latency plot of QA Farm system rack6slot8.osadl.org">
