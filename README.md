README for Unique Line Extractor & Merger
  Introduction

  Welcome to the Unique Line Extractor repository! This Python script is a powerful tool designed for crawling through directories and subdirectories, extracting unique lines from text files, and generating summarized output files. 
  It's crafted to handle large datasets efficiently and ensure optimal performance without exceeding system memory limits.
  
  Key Features

  Robust Directory Crawling: Recursively processes text files in specified directories and their subdirectories.
  
  Unique Line Extraction: Extracts unique lines from text files, eliminating duplicates and unwanted formats.
  
  Optimized for Memory Efficiency: Utilizes batch processing to manage memory usage effectively, suitable for large files.
  
  Customizable Settings: Offers command-line arguments for adjusting the start directory, output file naming, and maximum memory usage.
  
  Progress Monitoring: Features real-time progress indicators for each file being processed.
  
  Specialized Gmail Address Filtering: Excludes lines containing Gmail addresses. 
  
  (thats an adjust i temporary needed, if you dont, simply remove everything related to "gmail" in the code.
  
  Lines 45, 48, 49, 58, 84, 85, 96, 151, 159, 165, 202, 203)
  
  Effective Temporary File Handling: Manages and cleans up temporary files efficiently.
  
  Summary Output Generation: Produces a consolidated summary file in each processed directory.

System Requirements

  Python 3.x
  Required Libraries: os, argparse, tempfile, time, re, psutil, tqdm, send2trash

Installation Instructions

Clone the repository using the following command:

    git clone https://github.com/WhiteyCookie/unique-line-extractor.git

How to Use

  Execute the script via the command line, with the option to specify parameters such as the start directory, output file naming, and maximum memory usage. Without arguments it will of cource run its default configuration (see below),
  crawling recursively down its root dir, processing all .txt files in there.

Example Usage:

  Basic:

    python3 txt_file_mergeGPTv3.py

  Advanced:

    python txt_file_mergeGPTv3.py -s /path/to/start/dir -o output_filename -m 4

Command Line Arguments:

  -s / --start: Defines the start folder for file crawling (default: script's directory).
  
  -o / --output: Sets the base name for output files (default: '{folder_name}_summary').
  
  -m / --max-memory: Specifies the maximum memory usage in GB (default: 4 GB).



Contributing

  Your contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated. Fork the repository, make your changes, and submit a pull request.

Acknowledgments

  Special thanks to OpenAI's ChatGPT for its invaluable assistance during the development of this project. The guidance and support provided by ChatGPT were instrumental in addressing various coding challenges and enhancing the script's functionality.

License

  This project is released under the GNU General Public License (GPL), which provides copyleft for the distribution of free software. For more details, see the LICENSE file.
