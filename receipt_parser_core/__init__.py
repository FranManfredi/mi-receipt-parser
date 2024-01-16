from receipt_parser_core.config import *
from parse import *

def main():
  print("arranco")
  config = read_config()


  print("config", config)
  receipt_files = get_files_in_folder(config.receipts_path)
  print("receipt_files", receipt_files)
  stats = ocr_receipts(config, receipt_files)
  print("stats", stats)
  output_statistics(stats, None)

if __name__ == "__main__":
  main()