# Purem Benchmarks - High-Performance Mapping Operations
[![PyPI version](https://badge.fury.io/py/purem.svg)](https://pypi.org/project/purem/)
[![Architecture](https://img.shields.io/badge/sandbox-Apple%20Silicon-green)](https://developer.apple.com/documentation/apple-silicon)
[![License: BUSL-1.1](https://img.shields.io/badge/license-BUSL--1.1-blue.svg)](https://worktif.com/documents/terms-of-service-sandbox)

---

## 🚧 Service is temporarily unavailable

The service is currently unavailable due to scheduled maintenance.  
It will be **available starting from Monday, May 5th, 2025**.  
Thank you for your patience!

---

**The New Standard**  
Optimized for **x86-64**, **Intel**, and **ARM (Apple Silicon M1–M4)** servers.

---

## About

This repository contains **real-world benchmarks** for the Purem core technology, designed for **maximum performance testing** and **local validation**.

Purem now offers a **fully licensed and notarized sandbox binary** for **Apple Silicon M1 – M4** machines.

- **Unlimited**  
- **Unrestricted**  
- **No signup**  
- **No payment**  
- **No cloud dependencies**

You can **freely test and benchmark** Purem locally – the **same architecture**, the **same performance**, ready to run **directly on your Mac**.

---

## Key Highlights

- ⚡ **Full support for x86-64 and ARM64 (Apple M1–M4) architectures.**
- ⚡ **Production-grade benchmark scripts** included.
- ⚡ **Optimized Softmax computation** using **NumPy + Numba** (maximum CPU utilization).
- ⚡ **Parallelized and vectorized execution** for massive data sizes (millions to billions of elements).
- ⚡ **Accurate cost estimation for cloud and serverless environments** (AWS Lambda, Azure Functions, etc.).
- ⚡ **Focus on real hardware performance, not synthetic scores.**

---

## Getting Started

### Requirements

- Python 3.11+
- `purem`
- `numpy`
- `numba`
- `torch`
- `pandas`
- `scipy`
- `pytest`
- `matplotlib`
- MacBook or Mac server with Apple Silicon (M1–M4) – **or any x86-64 server** with supported Purem license.

#### About the Makefile
- 🧠 This project includes a Makefile for internal tasks like testing.
- 👉 You can run it if you like – it won't affect the project or cause any issues.

However, to perform full tests and benchmarks properly, please follow the official usage instructions. Just use the project as normal.

### Installation

Clone the repository:

```bash
git clone https://github.com/worktif/purem_sandbox.git
cd purem_sandbox
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Running Benchmarks

```bash
make test
```

Generates full performance plots under `src/purem_benchmarks/` showing a runtime vs input size.

Check it out: [CI/CD Purem Benchmarks](https://github.com/worktif/purem_sandbox/actions)

---


## 📊 Benchmark Highlights

Here’s a quick look at how Purem compares to existing Python ML libraries:

![Acceleration](./docs/assets/benchmark_acceleration_large.png)
*Acceleration (Purem vs NumPy, PyTorch, Numba)*

![OPS](./docs/assets/benchmark_ops_large.png)
*Operations per second on large inputs (log scale)*

![Stability](./docs/assets/benchmark_mean_large.png)
*Mean numerical error across large input sizes – lower values indicate higher numerical precision under load.*


---

## Licensing

- **Apple Silicon (M1–M4):**  
  The sandbox binary is **permanently free to use** – no registration required.  
  You can **fully develop, benchmark, and integrate** locally.

- **x86-64 Servers (Intel/AMD):**  
  A separate licensed version is available.  
  Please refer to the [Purem by Work TIF website](https://www.worktif.com) for more details.

---

## Important Dates

- 🗓️ **Sandbox Version Public Release:**  
  **April 28th, 2025**

---

## Why Benchmark with Purem?

By using the free sandbox, you can:

- Validate performance claims **locally**.
- Benchmark **your own models** with production-grade accuracy.
- Optimize cloud costs based on **real runtime data**.
- Prepare real-world production integrations **with no vendor lock-in**.

---

## Contact

For more information and licensing inquiries, please visit the [Purem by Work TIF Official Website](https://www.worktif.com).

---

> **Purem – Engineering the New Standard of Performance.**