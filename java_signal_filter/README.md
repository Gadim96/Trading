# Java Signal Filter Module

This module replicates a portion of the Python-based XGBoost signal pipeline in **pure Java**, emphasizing:

-  Object-oriented structure via `Signal.java`
-  Thread-safe filtering with `parallelStream()`
-  CSV I/O for clean integration with Python output/input
-  Optional concurrency via `CompletableFuture` for scalable processing

This implementation demonstrates **Java skills relevant to ATS and quant trading environments**, especially around type safety, parallelism, and modular code design.

---

## Files

| File | Purpose |
|------|---------|
| `SignalSelector.java` | Main entry point, loads CSV and runs filter |
| `SignalFilterTask.java` | Handles row-level filtering logic |
| `Signal.java` | Represents each signal object |
| `Utils.java` | CSV parser and helper methods |
| *(Optional)* `FilteredResultWriter.java` | Writes filtered signals to CSV (if implemented) |

---

## Run

Compile and run from VS Code terminal or CLI:

```bash
javac -d out src/**/*.java
java -cp out SignalSelector
```
