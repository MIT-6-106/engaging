import subprocess
import os
import argparse
import shutil
import time
import csv
import io
from datetime import datetime

# Get the current time and format it as a string
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Create a directory name based on the current time
directory_name = f"dir_{current_time}"

# Create the directory
os.makedirs(os.path.join("output", directory_name), exist_ok=True)
os.makedirs(os.path.join("error", directory_name), exist_ok=True)
os.makedirs(os.path.join("dataset", directory_name), exist_ok=True)

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
    default=10,
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
    default=15,
    help="Number of jobs in the SLURM array. Default is 50."
)
parser.add_argument(
    "--worker",
    type=int,
    default=2,
    help="Number of workers per training job"
)

parser.add_argument(
    "--update_frequency",
    type=int,
    default=60,
    help="Show partial ratings in this frequency. Default is every 60s"
)

parser.add_argument(
    "--binary",
    type=str,
    default=os.path.join("..", "bin", "leiserchess"),
    help="Use this binary to generate data"
)

# Parse the arguments
args = parser.parse_args()

# Access parsed arguments
sbatch_file = 'datagen.sh'
cores = args.cores
nodes = args.nodes
minutes = args.minutes
hours = args.hours
email = args.email
batch = args.batch
worker = args.worker
update_freq = args.update_frequency
out_dir = os.path.join('dataset', directory_name)
binary = args.binary

print('Dumping all outputs to', os.path.join('output', directory_name))
print('Dumping all errors to', os.path.join('error', directory_name))
print('Dumping dataset to', os.path.join('dataset', directory_name))
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
    f"module load python/3.9.4",
    f"python3 datagen.py --jobid $SLURM_ARRAY_TASK_ID --worker {worker} --out_dir {out_dir} --binary {binary}"
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
                game_update()
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


def game_update():
    try:
        cat_command = ["bash", "-c", f"cat {out_dir}/*.txt"]
        result_cat = subprocess.run(
            cat_command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(len(result_cat.stdout.split('\n')), 'rows of data generated')
    except subprocess.CalledProcessError as e:
        print(f"[WARN] {e.stderr.strip()}")

job_id = submit_job(sbatch_file)
print('')

if job_id:
    wait_for_job(job_id)
    game_update()
    try:
        merge_command = ["bash", "-c", f"cat {out_dir}/*.txt"]
        result_merge = subprocess.run(
            merge_command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        csv_like = io.StringIO(result_merge.stdout.strip())
        rows = [r for r in csv.reader(csv_like)]
        max_col = max(map(len, rows))
        print(max_col, ' columns generated for each row')
        dataset = [','.join(r) for r in rows if len(r) == max_col]
        dataset_path = os.path.join(out_dir, 'complete.txt')
        with open(dataset_path, 'w') as f:
            f.write('\n'.join(dataset))   
            print('dataset generated at', dataset_path)
    except Exception as e:
        print('Error occured while generating dataset:')
        print(e) 
