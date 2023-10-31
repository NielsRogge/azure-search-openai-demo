#!/bin/sh
python prepdocs.py \
--files "/Users/nielsrogge/Downloads/PDF_files/service_delivery/*" \
--category service_delivery \
--storageaccount stknowledge420a14f0 \
--container ict-loket \
--searchservice cognitive-search-420a14f0 \
--searchkey "your key" \
--index ict-loket-form-recognizer \
--openaihost azure \
--openaideployment openai-embedding-model \
--openaimodel text-embedding-ada-002 \
--openaikey "your key" \
--formrecognizerkey "your key"