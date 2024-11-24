import subprocess
import os
import argparse
import shutil
import time
from datetime import datetime

# Get the current time and format it as a string
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Create a directory name based on the current time
directory_name = f"dir_{current_time}"

# Create the directory
os.makedirs(os.path.join("output", directory_name), exist_ok=True)
os.makedirs(os.path.join("error", directory_name), exist_ok=True)
os.makedirs(os.path.join("pgnout", directory_name), exist_ok=True)


# Set up argument parser
parser = argparse.ArgumentParser(description="Generate and submit a SLURM sbatch file with custom parameters.")

parser.add_argument(
    "--cores",
    type=int,
    default=2,
    help="Number of cores/tasks to request. Default is 2."
)
parser.add_argument(
    "--nodes",
    type=int,
    default=1,
    help="Number of nodes to request. Default is 1."
)
parser.add_argument(
    "--minutes",
    type=int,
    default=45,
    help="Runtime in minutes to request. Default is 45."
)
parser.add_argument(
    "--hours",
    type=int,
    default=0,
    help="Runtime in hours to request. Default is 0."
)
parser.add_argument(
    "--email",
    type=str,
    required=True,
    help="Email address for SLURM notifications."
)
parser.add_argument(
    "--batch",
    type=int,
    default=50,
    help="Number of jobs in the SLURM array. Default is 50."
)
parser.add_argument(
    "--test",
    type=str,
    required=True,
    help="Test file for the autotester."
)

parser.add_argument(
    "--update_frequency",
    type=int,
    default=60,
    help="Show partial ratings in this frequency. Default is every 60s"
)

# Parse the arguments
args = parser.parse_args()

# Access parsed arguments
sbatch_file = 'tester.sh'
cores = args.cores
nodes = args.nodes
minutes = args.minutes
hours = args.hours
email = args.email
batch = args.batch
update_freq = args.update_frequency
test_file = os.path.join('pgnout', directory_name, 'test.txt')
shutil.copy(args.test, test_file) 

print('Dumping all outputs to', os.path.join('output', directory_name))
print('Dumping all errors to', os.path.join('error', directory_name))
print('Dumping all pgns to', os.path.join('pgnout', directory_name))
print('')

script = [
    "#!/bin/bash",
    f"#SBATCH -n {cores} #Request {cores} tasks (cores)",
    f"#SBATCH -N {nodes} #Request {nodes} node",
    f"#SBATCH -t 0-{str(hours).zfill(2)}:{str(minutes).zfill(2)} #Request runtime",
    f"#SBATCH -p sched_mit_hill #Run on sched_engaging_default partition",
    f"#SBATCH --mem-per-cpu=4000 #Request 4G of memory per CPU",
    f"#SBATCH -o output/{directory_name}/output_%j.txt #redirect output to output_JOBID.txt",
    f"#SBATCH -e error/{directory_name}/error_%j.txt #redirect errors to error_JOBID.txt",
    f"#SBATCH --array=1-{batch}",
    f"#SBATCH --mail-type=BEGIN,END #Mail when job starts and ends",
    f"#SBATCH --mail-user={email} #email recipient",
    f"module load jdk",
    f"make test TEST_FILE={test_file} BATCH_ID=$SLURM_ARRAY_TASK_ID"
]

with open(sbatch_file, 'w') as f:
    f.write('\n'.join(script))


def wait_for_job(job_id):
    while True:
        try:
            # Check if the job is still running or pending
            result = subprocess.run(
                ["squeue", "--job", job_id],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if job_id in result.stdout:
                print(f"Job {job_id} is still running...")
                rating_calculator()
            else:
                print(f"Job {job_id} has finished.")
                break
        except subprocess.CalledProcessError as e:
            print(f"Error checking job status: {e.stderr.strip()}")
            break
        
        # Wait for a few seconds before checking again
        time.sleep(update_freq)

def submit_job(sbatch_file):
    try:
        # Submit the job and capture the output
        result = subprocess.run(
            ["sbatch", sbatch_file],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Extract the Job ID from the output
        job_id = result.stdout.strip().split()[-1]
        print(f"Job submitted successfully. Job ID: {job_id}")
        return job_id
    except subprocess.CalledProcessError as e:
        print("Failed to submit SLURM job.")
        print(f"Error: {e.stderr.strip()}")
        return None


def rating_calculator(is_final=False):
    try:
        os.remove(os.path.join('pgnout', directory_name, 'test.pgn'))
    except: 
        pass

    try:
        # Combine all .pgn files into test.pgn
        cat_command = ["bash", "-c", f"cat pgnout/{directory_name}/*.pgn > pgnout/{directory_name}/test.pgn"]
        result_cat = subprocess.run(
            cat_command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if is_final:
            print(os.path.join('pgnout', directory_name, 'test.pgn'), "generated successfully.")

        # Run the shell command
        command = ["bash", "-c", f"cd pgn && ./pgnrate.tcl ../pgnout/{directory_name}/test.pgn"]
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if is_final:
            print(f"Final Rating:\n{result.stdout.strip()}")
        else:
            print(f"Partial Rating So Far:\n{result.stdout.strip()}")
            print('')
    except subprocess.CalledProcessError as e:
        if is_final:
            print("Failed to calculate rating.")
            print(f"Error: {e.stderr.strip()}")

job_id = submit_job(sbatch_file)
print('')

if job_id:
    wait_for_job(job_id)
    rating_calculator(True)
