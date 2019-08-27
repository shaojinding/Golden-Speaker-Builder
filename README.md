# Golden speaker Builder
This repository contains the code for Golden Speaker Builder.

## Server requirement (suggested)
*  8-core CPU
*  1TB harddrive
*  32GB memory

## Dependency
Nginx
*  [Installation documents](https://nginx.org/en/docs/install.html)
*  configuaration file: it is located at `dependency/nginx/nginx.conf`. Run `cp dependency/nginx/nginx.conf /etc/nginx/nginx.conf` to copy the config to the defualt nginx config directory.

Python
*  Python version: 2.7
*  Python dependencies: `pip install -r requirements.txt`

MATLAB
*  MATLAB version: R2016a

[MATLAB-Python API compilation](https://www.mathworks.com/help/matlab/matlab_external/install-matlab-engine-api-for-python-in-nondefault-locations.html)
*  `cd "matlabroot\extern\engines\python"`
*  `python setup.py install --prefix="/usr/lib/python2.7/site-packages"`

## Config the application
First, run `git clone https://github.tamu.edu/dshj940428/golden-speaker.git` to clone the repo to the servere. For example, on current GSB server, the directory to the repo is `/var/golden-speaker`.

Second, download and extract the needed files from [here]() to `/var/ARCTIC_v3`.

Third, config the MATLAB backend code. Run the following commands:

```
mkdir /var/gzhao
cd /var/gzhao
git clone https://github.tamu.edu/guanlong-zhao/vc-tools.git
cd /var/gzhao/vc-tools
git checkout gsb
```

Finally, configure the application by running:
```
sh deploy_script.sh
```

## Start the application
```
sh run.sh
```

## Stop the application
```
sh stop.sh
```
