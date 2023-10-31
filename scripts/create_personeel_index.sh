#!/bin/sh
python prepdocs.py \
"/Users/nielsrogge/Downloads/PDF_files/personeel/*" \
--category personeel \
--storageaccount stknowledge420a14f0 \
--container p-loket \
--searchservice cognitive-search-420a14f0 \
--searchkey "your-key" \
--index personeel-form-recognizer-basic \
--openaihost azure \
--openaideployment openai-embedding-model \
--openaimodel text-embedding-ada-002 \
--openaikey "your-key" \
--formrecognizerkey "your-key"