QUICK START GUIDE 
--------------------------------------------------------------------------------
This is a very brief overview of the autotester framework for the Engaging cluster. The overall framework is much more powerful and we would recommend reading the `README.md` for the `project4/tester` directory first. Here we will focus on how you can use it to run autotester on the Engaging clusters.

First ssh into the Engaging cluster as usual ([Link](https://engaging-web.mit.edu/eofe-wiki/logging_in/ssh/)). Assuming you have already cloned this repo in the engaging server

1. Run `module load jdk` to enable Java. Then cd into this directory and run `make clean && make` to compile all dependencies

2. Write a configuration file called `mytest.txt`. An example can be found in
   `tests/basic.txt`. The configuration file MUST end with `.txt` extension.

3. Run `module load python/3.9.4` to enable python. Run the autotester with

        $ python3 run.py --email "youremail@gmail.com" --test tests/mytest.txt

    (where `tests/mytest.txt` is the name of your test configuration file. You can also use `basic.txt` for starters). You can run
   
        $ python3 run.py --help
   
    to use more advanced testing features. 

5. You can see live ratings of the players every 60 seconds.

6. Once all games are over, you can view the `pgn` file at `pgnout/{game_dir}/test.pgn`. where `game_dir` is the unique game directory for each run. The output of `run.py` will also log the location of the `pgn` file.

CONFIGURATION FILE SYNTAX
--------------------------------------------------------------------------------
Here is a minimal configuration file example:

    ---------[ minimal_config.txt ]---------
	cpus = 2
	game_rounds = 10
	title = basic
	adjudicate = 400
	verbose = true

	player = player_1
	invoke = ../bin/leiserchess
	fis = 10 1

	player = player_2
	invoke = ../bin/leiserchess
	fis = 10 1

    ----------------[ snip ]----------------

This test file will actually run 10 \* 50 = 500 games when run with the `run.py` script because it will launch `50` (by default) jobs of the autotester in the engaging cluster. You can change the number of jobs by using `--batch` flag. Generally we would recommend going with the default configuration. Try not to use more than `200` jobs at a time.

If you would like to cancel the jobs that are running, you can run 

        $ scancel JOBID

where `JOBID` is the id of your job. You can find this id from the output of `run.py` as well as by running `squeue -u <kerb>` where the latter lists all the jobs you have running.


TRANSFERRING LEISERCHESS BINARY TO THE SERVER
--------------------------------------------------------------------------------

You may have noticed, there is no way to compile your code in the engaging server. For this we recommend changing your `player/Makefile` to this [Makefile](https://raw.githubusercontent.com/MIT-6-106/engaging/refs/heads/main/tester/compile/Makefile) and compiling your program locally with 

	$ make clean && make ENGAGING=1

and transferring the `leiserchess` binary to the engaging server by using `scp`. It could look something like

	$ scp /path/to/leiserchess/binary <kerb>@eofe7.mit.edu:/path/to/engaging/bin/<binary_name>

where replace the `kerb` with your kerb and and replace the `binary_name` with whatever name you want.
