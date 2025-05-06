# Does Anaphora Resolution Improve LLM Fine-Tuning for Meeting Summarization?
This project explores whether applying **anaphora resolution** as a preprocessing step improves the performance of **Large Language Model (LLM)** fine-tuning for meeting summarization tasks. The project leverages a simplified implementation of Mitkov’s Anaphora Resolution System (MARS) and tests its impact on the **T5-base** model using the **SAMSum** dialogue dataset.

The study shows that resolving ambiguous pronouns before fine-tuning leads to significantly improved summarization results across multiple ROUGE metrics.

## Dataset
The dataset used in this project is:
[SAMSum Corpus — Gliwa, B., Mochol, I., Biesek, M., & Wawer, A. (2019). *SAMSum Corpus: A Human-annotated Dialogue Dataset for Abstractive Summarization*. arXiv:1911.12237.](https://arxiv.org/abs/1911.12237)<br><br>

## Repository Structure

The repository contains the following files and directories:
- **mars.py**: Implementation of the simplified MARS system for anaphora resolution.

- **indicator.py**: Defines 14 heuristic scoring indicators used by MARS.

- **utils.py**: Utility functions used throughout the resolution process.

- **test.ipynb**: Demonstration notebook testing MARS on a small example.

- **preprocessing.ipynb**: Jupyter Notebook (for Google Colab) that loads and preprocesses the SAMSum dataset with anaphora resolution.

- **fine tune T5.ipynb**: Jupyter Notebook (for Google Colab) for fine-tuning the T5-base model with and without anaphora resolution.

- **main.ipynb**: Main orchestration or result analysis notebook.

- **README.md**: This README file.

- **Does_Anaphora_Resolution_Improve_LLM_Fine_Tuning_for_Meeting_Summarization_.pdf**: The full academic report on the methodology and findings.
 

 