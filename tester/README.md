QUICK START GUIDE 
--------------------------------------------------------------------------------
This is a very brief overview of the autotester framework for the Engaging cluster. The overall framework is much more powerful and we would recommend reading the `README.md` for the `project4/tester` directory first.

First ssh into the Engaging cluster as usual.

1. Run `module load jdk` to enable Java. Then run `make` to compile all dependencies

2. Write a configuration file called `mytest.txt`. An example can be found in
   `tests/basic.txt`. The configuration file MUST end with '.txt' extension.

3. Run `module load python/3.9.4` to enable python. Run the autotester with

        $ python3 run.py --email "youremail@gmail.com" --test tests/mytest.txt

    (where `tests/mytest.txt` is the name of your test configuration file. You can also use `basic.txt` for starters). You can run 
        $ python3 run.py --help
    to use more advanced testing features. 

4. You can see live ratings of the players every 60 seconds.

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

This test file will actually run 10 \* 50 = 500 games when run with the `run.py` script because it will launch the autotester in `50` jobs (by default) in the engaging cluster. You can change the number of jobs by using `--batch` flag. Generally we would recommend going with the default configuration. Try not to use more than `200` jobs at a time.

If you would like to cancel the jobs that are running, you can run 
   $ scancel <JOBID>

where `JOBID` is the id of your job. You can find this id from the output of `run.py` as well as by running `squeue -u <kerb>` where the latter lists all the jobs you have running.
