# Ultimate DuckDB Setup

This document describes how to obtain a “decked out” DuckDB setup with as many built-in and external extensions as possible. It covers installing DuckDB from source, including optional modules, plus community or third-party extensions. 

## 1. Clone DuckDB Repo

You can obtain the source from the official GitHub repository:

```
git clone https://github.com/duckdb/duckdb.git
cd duckdb
```

## 2. Configure and Enable Built-In Extensions

DuckDB includes many built-in extensions that can be enabled at build time. Some examples:  
• parquet  
• httpfs  
• json  
• icu  
• fts (full-text search)  
• tpcds / tpch (benchmarks)  
• visualizer (graphical query plans)  
• sqlsmith (random query generator)  

When building DuckDB from source with CMake, you can enable these extensions, for example:

```
cmake -DENABLE_JSON=1 \
      -DENABLE_PARQUET=1 \
      -DENABLE_HTTPFS=1 \
      -DENABLE_HTTPS=1 \
      -DENABLE_FTS=1 \
      -DENABLE_ICU=1 \
      -DENABLE_JEMALLOC=1 \
      -DENABLE_TPCH=1 \
      -DENABLE_TPCDS=1 \
      -DENABLE_VISUALIZER=1 \
      -DENABLE_SQLSMITH=1 \
      ..
make -j8
```

(Optional flags vary. You can see all by running `ccmake ..` or reviewing the main [build docs](https://github.com/duckdb/duckdb/blob/master/docs/development/build.md).)

## 3. Community / Third-Party Extensions

Beyond built-in ones, you can find interesting projects that plug into DuckDB:

1. [Spatial Extensions (spatialite, geos, proj)](https://github.com/duckdblabs/duckdb_spatial)  
   • This adds geometry/geography types, plus spatial indexing and queries  
2. [DuckDB Python Morsels](https://pypi.org/project/duckdb/)  
   • Official Python package with optional extras  
3. [DuckDB Node.js Bindings](https://github.com/duckdb/duckdb/tree/master/tools/node)  
   • Let you run DuckDB in Node  
4. [DuckDB Ruby Bindings](https://github.com/suketa/duckdb_ruby)  
   • Example Ruby integration  
5. [Wasmer/WASI builds](https://github.com/duckdb/duckdb-wasm)  
   • For running DuckDB in WebAssembly contexts  

## 4. Fuzzing the Types

DuckDB’s `sqlsmith` extension does random query generation for crash or bug detection. To build it:

```
cmake -DENABLE_SQLSMITH=1 ..
make -j8
```

Then you can run `./build/debug/duckdb_sqlsmith` or the installed tool to fuzz queries across varied data types.

## 5. Automatic “Everything” Script Example

Below is a pseudo-script showing how you might build DuckDB with maximum features. Place this script in `duckdb_build_all.sh` (within topoi-mcp, for example), then run it from the command line.

```bash
#!/usr/bin/env bash

set -e

# 1. Clone
git clone https://github.com/duckdb/duckdb.git duckdb-all
cd duckdb-all

# 2. Create build directory
mkdir build
cd build

# 3. Configure with many extensions
cmake -DENABLE_JSON=1 \
      -DENABLE_PARQUET=1 \
      -DENABLE_HTTPFS=1 \
      -DENABLE_HTTPS=1 \
      -DENABLE_ICU=1 \
      -DENABLE_FTS=1 \
      -DENABLE_TPCDS=1 \
      -DENABLE_TPCH=1 \
      -DENABLE_JEMALLOC=1 \
      -DENABLE_VISUALIZER=1 \
      -DENABLE_SQLSMITH=1 \
      -DENABLE_UNICODE=1 \
      ..

# 4. Build
make -j$(nproc || sysctl -n hw.physicalcpu || echo 4)

# 5. Run tests (optional)
ctest --output-on-failure

echo "DuckDB built with maximum extensions!"
```

## 6. Using DuckDB

Once built, you’ll have a `duckdb` binary in the `build` folder. For example:

```
./duckdb
```

You can load built-in extensions using SQL:

```sql
.load httpfs
.load parquet
.load json
.load fts
-- etc.
```

## 7. Further Ideas

• Investigate [DuckDB Labs repos](https://github.com/duckdblabs) for more specialized (potentially experimental) plugins and integrations.  
• Add geospatial support with DuckDB Spatial, or other domain-specific features.  
• If you want “fuzzing the types” in a dedicated sense, set up [SQLSmith logs](https://github.com/duckdb/duckdb/blob/master/tools/sqlsmith/README.md).  

## 8. References

• [DuckDB Official Docs](https://duckdb.org/docs/)  
• [DuckDB Source Build Instructions](https://github.com/duckdb/duckdb/blob/master/docs/development/build.md)  
• [DuckDB Labs GitHub Org](https://github.com/duckdblabs)  

With these steps, you should have a “decked out” DuckDB that can handle multiple file formats (Parquet, JSON, CSV, etc.), run over HTTP or local FS, do textual search (FTS), run random query fuzzing (SQLSmith), and more. Experiment with third-party or community plugins to extend DuckDB even further.
