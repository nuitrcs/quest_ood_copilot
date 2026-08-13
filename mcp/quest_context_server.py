#!/usr/bin/env python3
"""
MCP server providing Quest HPC cluster context to GitHub Copilot.

Install dependencies:
  module load mamba
  mamba create --prefix /software/2025/github_copilot_gui/mcp/env python=3.11 pip -y
  /software/2025/github_copilot_gui/mcp/env/bin/pip install mcp
"""
import asyncio
import json
from mcp.server.mcpserver import MCPServer

server = MCPServer(name="quest-cluster-context")

CLUSTER_CONTEXT = {
    "cluster": {
        "name": "Quest",
        "institution": "Northwestern University",
        "support": "Research Computing and Data Services (RCDS)",
        "documentation": "https://rcdsdocs.it.northwestern.edu",
        "scheduler": "SLURM",
    },
    "login": {
        "hostname": "login.quest.northwestern.edu",
        "username": "Northwestern NetID (lowercase)",
        "port": 22,
        "methods": [
            "SSH: ssh <netid>@login.quest.northwestern.edu",
            "FastX desktop client (for GUI apps)",
            "FastX browser: https://login.quest.northwestern.edu:3300 (campus or GlobalProtect VPN required)",
        ],
        "login_node_limits": "4 cores and 6 GB RAM per user — for job submission only, not computation",
    },
    "partitions": {
        "general_access": [
            {"name": "short",    "max_walltime": "4:00:00",   "use_case": "Jobs completing within 4 hours; broadest node access"},
            {"name": "normal",   "max_walltime": "48:00:00",  "use_case": "4-hour to 2-day jobs; moderate node availability"},
            {"name": "long",     "max_walltime": "168:00:00", "use_case": "2-7 day jobs; limited node access"},
            {"name": "gengpu",   "max_walltime": "48:00:00",  "use_case": "GPU jobs only"},
            {"name": "genhimem", "max_walltime": "48:00:00",  "use_case": "Jobs requiring more than 473 GB memory per node"},
        ],
        "priority_access": (
            "Dedicated purchased nodes; partition name is typically the account name or 'buyin'. "
            "Custom time limits per allocation. Priority Access accounts cannot submit to General Access partitions."
        ),
    },
    "accounts": {
        "general_access_format": "pXXXX (Research I) or eXXXX",
        "priority_access_format": "bXXXX",
        "how_to_check": "Run 'groups' on a login node, or visit the ColdFront portal",
        "required_flags": "--account and --partition are required for every job submission",
    },
    "node_hardware": [
        {"name": "quest10",      "cpus_per_node": 52,  "memory_gb": 166, "constraint": "quest10"},
        {"name": "quest10 GPU",  "cpus_per_node": 52,  "memory_gb": 166, "constraint": "quest10,pcie"},
        {"name": "quest11",      "cpus_per_node": 64,  "memory_gb": 221, "constraint": "quest11"},
        {"name": "quest12",      "cpus_per_node": 64,  "memory_gb": 221, "constraint": "quest12"},
        {"name": "quest12 GPU",  "cpus_per_node": 64,  "memory_gb": 473, "constraint": "quest12,sxm"},
        {"name": "quest13",      "cpus_per_node": 128, "memory_gb": 473, "constraint": "quest13"},
        {"name": "quest13 GPU",  "cpus_per_node": 64,  "memory_gb": 976, "constraint": "quest13,sxm"},
    ],
    "gpus": {
        "types": [
            {"model": "NVIDIA A100", "memory_gb": "40 or 80 depending on node", "gres_flag": "gpu:a100:N"},
            {"model": "NVIDIA H100", "memory_gb": 80,                           "gres_flag": "gpu:h100:N"},
        ],
        "partition": "gengpu",
        "max_gpus_per_user": 8,
        "sxm_constraint": "Use --constraint=sxm for NVLink multi-GPU or 80 GB A100 nodes",
        "cuda_recommendation": "CUDA 12.2+ recommended; compile with sm_80 (A100) and sm_90 (H100)",
        "note": "--mem specifies system RAM only; GPU memory is allocated automatically",
    },
    "storage": [
        {
            "path": "/home/<netid>",
            "quota": "80 GB",
            "file_limit": "10 million",
            "backed_up": True,
            "backup": "nightly, 1-week recovery window",
            "shared": False,
            "retention": "deleted when NetID expires",
            "use_case": "Scripts, logs, small software installs",
        },
        {
            "path": "/projects/<account-name>",
            "quota": "1 TB (Research I) or 2 TB (Research II); additional storage purchasable",
            "file_limit": "50 million",
            "backed_up": False,
            "shared": True,
            "use_case": "Large datasets, frequently-accessed files, collaborative work",
        },
        {
            "path": "/scratch/<netid>",
            "quota": "5 TB (flash SSD)",
            "file_limit": "5 million",
            "backed_up": False,
            "retention": "auto-deleted 30 days after last modification or access",
            "shared": "can be shared if configured",
            "use_case": "Temporary files, GPU workflows, staging data",
        },
    ],
    "data_transfer": {
        "recommended": "Globus (best for large files and interrupted transfers)",
        "transfer_node": "qdtn01 — supports sftp, scp, aspera, wget",
        "tools": [
            {"tool": "scp",    "best_for": "Small one-off transfers up to ~1 GB", "hostname": "login.quest.northwestern.edu"},
            {"tool": "rsync",  "best_for": "Syncing folders with small files up to ~1 GB", "hostname": "login.quest.northwestern.edu"},
            {"tool": "wget",   "best_for": "Downloading from external HTTP/HTTPS servers directly to Quest"},
            {"tool": "aws s3", "module": "awscli/2.15.22"},
            {"tool": "gsutil", "module": "gcloud/522.0.0"},
        ],
        "size_guidelines": {"ondemand_file_explorer": "under 5 GB", "analytics_nodes": "under 500 MB"},
    },
    "software_modules": {
        "system": "LMOD",
        "commands": {
            "list_all":    "module avail",
            "search":      "module avail <name>",
            "load":        "module load <name>/<version>",
            "list_loaded": "module list",
            "unload_all":  "module purge all",
            "preview":     "module display <name>",
        },
        "best_practice": "Always specify the version explicitly, e.g. 'module load matlab/r2024a'",
        "notable_software": ["MATLAB", "Python", "R", "RStudio", "VASP", "Abaqus", "Knitro", "AlphaFold"],
    },
    "slurm_tips": {
        "memory_profiling": (
            "Submit a test job with --mem=0 --nodes=1, then check usage with 'seff <jobid>'. "
            "Set production memory to actual_usage * 1.10."
        ),
        "priority": "Fairshare score is based on recent usage; priority decays over ~1 month of inactivity.",
        "job_dependencies": "Use --dependency=afterok:<jobid> to chain jobs sequentially.",
        "common_errors": [
            "Priority Access accounts cannot submit to General Access partitions.",
            "Requested walltime must not exceed partition maximum.",
            "Jobs exceeding requested RAM are terminated immediately with OUT_OF_MEMORY.",
        ],
        "useful_commands": {
            "view_my_jobs":       "squeue -u <netid>",
            "job_efficiency":     "seff <jobid>",
            "cancel_job":         "scancel <jobid>",
            "modify_pending_job": "scontrol update job=<jobid> partition=<value>",
            "historical_usage":   "sacct -X -j <jobid>",
        },
    },
}


@server.tool()
def get_cluster_overview() -> str:
    """Returns a general overview of the Quest HPC cluster including name, institution, scheduler, and login information."""
    return json.dumps({**CLUSTER_CONTEXT["cluster"], **CLUSTER_CONTEXT["login"]}, indent=2)


@server.tool()
def get_partitions() -> str:
    """Returns all available SLURM partitions on Quest, their maximum walltimes, and intended use cases."""
    return json.dumps(CLUSTER_CONTEXT["partitions"], indent=2)


@server.tool()
def get_node_hardware() -> str:
    """Returns hardware specifications for each node generation on Quest including CPU count, memory, and constraint values."""
    return json.dumps(CLUSTER_CONTEXT["node_hardware"], indent=2)


@server.tool()
def get_gpu_info() -> str:
    """Returns details about GPU types available on Quest, how to request them, and relevant SLURM flags."""
    return json.dumps(CLUSTER_CONTEXT["gpus"], indent=2)


@server.tool()
def get_storage_info() -> str:
    """Returns details about the three storage locations on Quest: home, projects, and scratch — including quotas, backup status, and retention policies."""
    return json.dumps(CLUSTER_CONTEXT["storage"], indent=2)


@server.tool()
def get_data_transfer_info() -> str:
    """Returns recommended tools and methods for transferring data to and from Quest."""
    return json.dumps(CLUSTER_CONTEXT["data_transfer"], indent=2)


@server.tool()
def get_software_modules() -> str:
    """Returns information about the LMOD software module system on Quest, key commands, and notable available software."""
    return json.dumps(CLUSTER_CONTEXT["software_modules"], indent=2)


@server.tool()
def get_slurm_tips() -> str:
    """Returns SLURM best practices, memory profiling workflow, job dependency patterns, common errors, and useful commands for Quest."""
    return json.dumps(CLUSTER_CONTEXT["slurm_tips"], indent=2)


@server.tool()
def get_account_info() -> str:
    """Returns SLURM account and allocation naming conventions on Quest and how to look up available accounts."""
    return json.dumps(CLUSTER_CONTEXT["accounts"], indent=2)


if __name__ == "__main__":
    asyncio.run(server.run_stdio_async())
