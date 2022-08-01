# Residual deformation
Simple GUI to analyze residual deformations from experiments. This is an old project which I used to create GUI by 
using tkinter.

## To Anička
* install [anaconda](https://www.anaconda.com) or [miniconda](https://docs.conda.io/en/latest/miniconda.html) with python
* download zip of this repo (or use git as described bellow)
* unzip
* open `cmd` in the folder `residual_deformations` 
* run `python residual_deformations.py`
* GUI should appear -> follow `Steps to analyze image` bellow
## How to run the program
* `git clone https://github.com/olisicky/residual_deformation.git`
* Optional: create new virtual environment
* Install packages `pip install -r requirements.txt`
* `python residual_deformations.py`

## Experiments
Experiments are performed at Faculty of Mechanical Engineering, Institute of solid mechanics, mechatronics and 
biomechanis.
* experiment is described as an appendix in my thesis [TODO]()

## Steps to analyze image
* `Upload image` - find the image which should be analyzed
* Select if the image is from Basler camera and setup or do calibration
* `Select boundary`
    * You should click and drag around the region of interest
    * Press `ESC` or `ENTER`
* Left click some points on the outer boundary of the segment
    * points should start and end on the edges to have a whole segment
* Press `a`
* Left click some points on the inner boundary
    * points should start and end on the edges to have a whole segment
* select number of points and press `OK`
* Select if the segment is cutted or full ring
* Press `Draw results`
    * image of with boundaries should appear
    * results are showed and saved with the same name as is the filename
* Once the segment is analysed the window needs to be closed (file -> exit) and the process needs be unfortunatelly repeated for new sample
