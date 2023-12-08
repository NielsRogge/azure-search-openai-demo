# create index "ict-loket-form-recognizer-basic" on ML6's subscription
python prepdocs.py \
"/Users/nielsrogge/Downloads/PDF_files/service_delivery/*" \
--category service_delivery \
--storageaccount stknowledge420a14f0 \
--container ict-loket \
--searchservice cognitive-search-420a14f0 \
--searchkey "" \
--index ict-loket-form-recognizer-basic \
--openaihost azure \
--openaideployment openai-embedding-model \
--openaimodel text-embedding-ada-002 \
--openaikey "" \
--formrecognizerkey "" \
--verbose