# Urge Purge

Remember to set up the python virtual environment and install the required packages.

## Setup
You will require Python 3 and Node.js to run.  They will require additional packages to be installed at `./docs`.  Therefore, the first command one should run is simply:

```
$ cd docs
```

### Python 3
It is recommended to use `virtualenv`.
```
(docs) $ pip install pyqt5
```

### Node.js
It is recommended to save packages locally with `npm install --save`.
```
$ npm install --save request
$ npm install --save httpProxy
$ npm install --save bodyParser
$ npm install --save express
```

## Run
To run, simply run `main.js` using Node.js.
```
$ cd docs
$ . bin/activate
(docs) $ node main.js
```
To stop the server, simply press Ctrl-C.
