# Project 4 Training Script

## Usage
First make sure you have set up the engaging server to use tester framework. The data generation process is fairly similar.

Now install `numpy` if it's not installed already

    $ module load python/3.9.4
    $ pip install numpy --user

Then run 

    $  python3 run.py --minutes 10 --email youremail@gmail.com --binary ../bin/leiserchess --batch 15
    

This will run the training script for 10 minutes and with 15 jobs and generate the dataset into `dataset/{game_dir}/complete.txt`. The output of `run.py` will log the `game_dir`. Here `../bin/leiserchess` is the path to the binary that will be used to generate the dataset, but feel free to change it accordingly. You will need to use `scp` to transfer the binary from your local machine to the engaging server. See the tester directory `README.md` for reference.

## Training the weights

Engaging server is not suitable for training weights. You can download the dataset from the engaging server using scp (see the tester directory) and run the training script on google colab or a local machine. 
