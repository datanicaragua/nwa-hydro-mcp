@workspace

**ACT AS:** Senior Technical Architect & Repository Maintainer.
**GOAL:** Perform a strict "Pre-Commit Audit" of the current file structure and generate a cleanup script to align it with our architectural standards.

**CONTEXT - THE STANDARD:**
Please read the file `docs/technical_notes/NT_000_Project_Charter_and_Architecture_v1.0.md` carefully. This file contains the definitive "Directory Structure" we must follow.

**THE PROBLEM (Observation from current workspace):**
I see inconsistencies in the current layout compared to the NT_000 standard:

1. There is a `src/strategy` folder that seems incorrect (Source code shouldn't contain PDF strategy files).
2. There are redundant files like `stack-gemini.md` in multiple locations.
3. We need to consolidate all non-code assets into `docs/`.

**ACTION REQUIRED:**

1. **Analyze:** Compare the current file tree against the structure defined in `NT_000`.
2. **Plan:** Identify which files need to be moved, renamed, or deleted to achieve a pristine state.
3. **Execute:** detailed PowerShell script (for Windows) that:
   - Moves `Plan_Estrategico_v1.0.pdf` and any `.md` strategy files from `src/strategy` to `docs/strategy`.
   - Moves `stack-gemini.md` to `.ai/context/` (or deletes duplicates if one exists).
   - Deletes the incorrect `src/strategy` folder after emptying it.
   - Ensures `src/nwa_hydro` only contains Python code (`.py`).
   - Ensures `data/` contains the `local_station.csv` (if it exists) or keeps the folder.

**OUTPUT:**
Provide **ONLY** the PowerShell script to fix the structure. I will run it immediately.
