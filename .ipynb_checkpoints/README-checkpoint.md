# jss3_tools

This repository brings together tools used in the environment of JAXA's JSS3 supercomputer.
Assume that the environment described in [this document](https://docs.google.com/document/d/1wmKQ9R1ABFOihh9hA9_BJLaaVsxsoY-5thLAU0HZtQI/edit#heading=h.h7c9xt3ercmx) is created in JSS3.


## Usage
- `build_jupyter.py`
    - This function starts a jupyter server on RURI based on the prepared singularity environment, and outputs standard ssh commands required for port forwarding in combination with the assigned node ID and the specified port. You must have jupy, an anaconda virtual environment like jupyter lab, installed as described in the environment setup documentation.
    - The way for executing is 
    ```
    $ python build_jupyter.py
    ```

## Tutorial of the litebird_sim　
In the [example](./example), I put a sample code of the [litebird_sim](https://github.com/litebird/litebird_sim/tree/master), which can be executed with JSS3.　
The litebird_sim anaconda virtual environment is required for execution.

- `get_hitmap_serial.py`
    - Since this is a serial computation code without MPI parallel computation, it can be executed independent of the environment. It is placed here for comparison with `get_hitmap_parallel.py`. 
    - The way for executing is 
    ```
    (lbs_env) $ python get_hitmap_serial.py
    ```
    
- `get_hitmap_parallel.py`
    - The code is for MPI parallel computation with the same result for serial computation. A batch job script must be submitted to RURI to execute this code. The code to submit the job is [run_parallel.py](./example/run_parallel.py), written in python. The required script is generated in the python code, and the job is submitted to the job scheduler using subprocess. The number of nodes, cores, memory requirements, etc. are set in this code. 
    - The way for executing is 
    ```
    (lbs_env) $ python run_parallel.py
    ```

    