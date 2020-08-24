## Using python-copasi with AWS Lambda
This basic example demonstrates the use of `python-copasi` for use with AWS lambda. It will 

* create a python3.8 layer that pulls python-copasi
* contain a sample function, that when invoked by a trigger, will take the given COPASI file, and simulate it, writing the output into a result bucket.

