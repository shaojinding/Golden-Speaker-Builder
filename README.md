# Golden speaker Builder
This repository contains the code for Golden Speaker Builder.

## Server requirement (suggested)
*  >8-core CPU
*  >1TB harddrive
*  >32GB memory

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

