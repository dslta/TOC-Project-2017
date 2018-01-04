#!/bin/bash

for file in *.pdf
do
  echo "Converting $file to txt file"
  pdfx $file -t -o ../txt/$(echo $file | cut -f 1 -d '.').txt
done
