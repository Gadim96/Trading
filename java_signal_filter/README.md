# Java Signal Filter Module

This module replicates part of the Python XGBoost signal pipeline using pure Java. It includes:

- OOP-based signal object (`Signal.java`)
- Thread-safe filtering using `parallelStream()`
- CSV I/O for integration with Python pipeline
- Optional concurrency extensions via `CompletableFuture`

This showcases Java skills relevant to ATS and quant environments.

## Run

Compile and run via VS Code or terminal:

```bash
javac -d out src/**/*.java
java -cp out Main
```
