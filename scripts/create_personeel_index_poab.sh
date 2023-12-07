#!/bin/sh
python prepdocs.py \
"/Users/nielsrogge/Downloads/PDF_files/personeel/*" \
--category personeel \
--storageaccount stknowledge877b5c5a \
--container p-loket \
--searchservice cognitive-search877b5c5a \
--searchkey "your-key" \
--index personeel-form-recognizer-basic \
--openaihost azure \
--openaideployment openai-embedding-model \
--openaimodel text-embedding-ada-002 \
--openaikey "your-key" \
--formrecognizerkey "your-key" \
--verbose