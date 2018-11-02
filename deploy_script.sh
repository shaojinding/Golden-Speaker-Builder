mkdir static/ARCTIC
cp -r ../ARCTIC_v3/cbl static/ARCTIC
cp -r ../ARCTIC_v3/gma static/ARCTIC
python manage.py collectstatic
python manage.py migrate
python populate_gsb_ppg_gmm.py
# cp -r external/* SABR/toolkits/
mkdir data
mkdir data/output_wav
mkdir data/sabr
mkdir data/cache
mkdir data/pitch
mkdir data/recordings
mkdir data/pitch_model
