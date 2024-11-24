# Project 4 Training Script

## Usage
First, ssh into the engaging server as usual. Then install `numpy` if it's not installed already

    $ module load python/3.9.4
    $ pip install numpy --user

Then run 

    $ python3 run.py --minutes 45 --email youremail@gmail.com
    

This will run the training script for 45 minutes and generate the dataset into `dataset/{game_dir}/complete.txt`. The output of `run.py` will log where the dataset will be generated.

## Training the weights

Engaging server is not suitable for training weights. You can download the dataset from the engaging server using scp (see the tester directory) and run the training script on google colab or a local machine.
