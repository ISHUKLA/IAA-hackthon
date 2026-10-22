# Competition input data

The 11 original Parquet inputs for **IAA AI Assisted Hackathon 2026 – Part 1** are stored unchanged in [public/](public/) through Git LFS.

Provider: **International Actuarial Association**. Source: [Kaggle competition Data page](https://www.kaggle.com/competitions/iaa-ai-assisted-hackathon-2026-part-1/data). The Data page license label recorded on 22 October 2026 is [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). Source ownership and terms are retained; no changes have been made to the supplied files. The [competition rules](https://www.kaggle.com/competitions/iaa-ai-assisted-hackathon-2026-part-1/rules), including their access and redistribution restrictions, also apply.

[public/manifest.json](public/manifest.json) records the filename, byte size and SHA-256 checksum of every input. Together the inputs occupy 198,159,846 bytes (188.98 MiB). Repaired tables, model objects and generated predictions remain local outputs.

## Download and use

Install Git LFS before cloning. In an existing checkout, run:

```sh
git lfs install
git lfs pull --include="data/public/*.parquet"
export IAA_DATA_DIR="$PWD/data/public"
```

If the Parquet files contain only a short text pointer, Git LFS has not downloaded their content yet. Treat the input copies as read-only and write derived tables to outputs/.
