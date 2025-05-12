#!/bin/bash

# Папка с файлами
source_dir=$1

# Файл, куда будет записан результат
output_file=$2

# Очистить или создать новый файл
> "$output_file"

# Обработка каждого файла в папке
for file in "$source_dir"/*; do
  if [ -f "$file" ]; then
    # Получить имя файла
    filename=$(basename "$file")

    # Записать название файла в выходной файл
    echo "# $filename" >> "$output_file"

    # Записать содержимое файла в выходной файл
    cat "$file" >> "$output_file"

    # Добавить разделитель
    echo -e "\n# end of $filename\n" >> "$output_file"
  fi
done
