# Script that will run on Floydhub to kick off training

set -x

export PYTHONPATH=/floyd/home
echo $PYTHONPATH
# ugh I have to do this otherwise I get the error `Please use the NLTK Downloader to obtain the resource:`
python -c "import nltk; nltk.download('punkt')"
python datasets/html/dataset.py --data_name=$1 && chmod +x ./my-scripts/html/train.sh && time ./my-scripts/html/train.sh $1 $2
