# Performance Measures for Message Digests, Symmetric and Asymmetric Cryptography

This project is part of the S**ecurity and Privacy** course at the **Faculty of Sciences, University of Porto**,
developed to explore and better understand common encryption and decryption methods.

## Setup and Installation

### 1. Create and Activate a Virtual Environment

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## Model Execution

### AES Counter Mode

The script uses the cryptography library to implement the method.

A benchmarking layer isolates the cryptographic operations by pre-loading data into memory, ensuring little noise in the results. The system returns runtimes in microseconds utilizing the `timeit` module to clock the execution and iterate 100 times over each file size.

Finnaly the code utilizes `utils.py` to calculate the statistics while `matplotlib` is used to generate the graphs.


Run the main file

```python
python aes_ctr_crypto.py
```

Rename the generated graph if saving multiple runs is needed. (Line 119)

```python
plot.savefig('aes_combined_plot_random_2.png', bbox_inches='tight', dpi=300) # Rename graph for every rerun
```

Alternate between run_performance_test() and run_performance_test_random() to switch between the previously generated files and newly generated random data. (Line 178)

```python
if __name__ == "__main__":
    run_performance_test() # Alternate between run_performance_test() and run_performance_test_random()
```
