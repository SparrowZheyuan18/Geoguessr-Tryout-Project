#!/bin/bash
#SBATCH --job-name=extract_clues      # 作业名称
#SBATCH --output=extract_clues.out     # 标准输出和错误输出文件
#SBATCH --error=extract_clues.err      # 错误输出文件
#SBATCH --time=05:00:00           # 运行时间 (HH:MM:SS)
#SBATCH --partition=clip         # 分区名称
#SBATCH --account=clip       # 账号名称


source ~/miniconda3/etc/profile.d/conda.sh

conda activate geoguessr

python main.py