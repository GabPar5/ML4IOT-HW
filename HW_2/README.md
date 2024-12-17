-1st model: Log-Mel preprocessing args with callbacks, CNN with DepthWise Conv2D, no weigths-pruning ------> 54.6% acc, 548kB size

-2nd model: Log-Mel preprocessing args(64 bin, lower_freq = 0, upper_freq = 8000) with callbacks, CNN without DephtWise Conv2D, no weigths-pruning ------> 63.8%, 1162.1 kB 

-3rd model: Log-Mel preprocessing args(64 bin, lower_freq = 20, upper_freq = 4000) with callbacks, CNN without DephtWise Conv2D, no weigths-pruning ------> 77.4%, 1162.1 kB 


