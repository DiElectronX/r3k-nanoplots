# r3k-nanoplots

Super simple framework for managing NanoAOD file plots. 

Format a `.yml` file with the configuration of `plot_list.yml`. Some parameters are optional but the core bits of information like input files, branches, binning, etc. must be set. Then just runner the `plotter.py` script like below. Make sure to label and push any specific plotting configurations to keep track of them for the publication process.

Only simple histograms are currently configurable. More options will be added as more edits need for be made to the AN/paper.

## Running the script
```
python3 plotter.py -c plot_list.yml
```
