import os

from settings import OUTPUT_PATH

output_path = os.path.join(OUTPUT_PATH, 'filename.txt')

with open(output_path, 'w') as file:
    file.write('Writing a file, woohoo!')
