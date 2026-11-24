import subprocess
import sys

from data_generation.config import BASE_DIR, VALIDATION_DIR

DATA_GENERATION_DIR = BASE_DIR / "data_generation"

MAX_ATTEMPTS = 3

GENERATION_SCRIPTS = ["customers.py",
                    "accounts.py",
                    "transactions.py"]

VALIDATION_SCRIPT = "validate_data.py"

def run_script(script_path):
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=BASE_DIR
    )
    return result.returncode

def clear_validation_outputs():
    for file in VALIDATION_DIR.glob("*.csv"):
        file.unlink()

def generate_data():
    for attempt in range(1, MAX_ATTEMPTS + 1):
        
        print(f"\n{"-"*50}")
        print(f"DATA GENERATION ATTEMPT {attempt}/{MAX_ATTEMPTS}")
        print(f"\n{"-"*50}")
        
        clear_validation_outputs()
        for script_name in GENERATION_SCRIPTS:
            script_path = DATA_GENERATION_DIR / script_name
            print(f"\nRunning {script_name}...")
            exit_code = run_script(script_path=script_path)
            
            if exit_code != 0:
                print(f"\nERROR: {script_name} failed.")
                print("Data generation stopped.")
                sys.exit(1)
                
        validation_path = DATA_GENERATION_DIR / VALIDATION_SCRIPT
        print("\nRunning Data Validation...")
        exit_code = run_script(validation_path)

        if exit_code == 0:
            print("\n" + "=" * 50)
            print("DATA GENERATION SUCCESSFUL")
            print("ALL VALIDATION CHECKS PASSED")
            print("=" * 50)

            sys.exit(0)

        print(f"\nValidation failed on attempt {attempt}.")

        if attempt < MAX_ATTEMPTS:
            print("Regenerating all datasets...")
        else:
            print("\nMaximum attempts reached.")
            print("DATA GENERATION FAILED.")
            sys.exit(1)
            
if __name__ == "__main__":
    generate_data()