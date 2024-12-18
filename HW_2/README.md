-1st model: Log-Mel preprocessing args with callbacks, CNN with DepthWise Conv2D, no weigths-pruning ------> 54.6% acc, 548kB size

-2nd model: Log-Mel preprocessing args(64 bin, lower_freq = 0, upper_freq = 8000) with callbacks, CNN without DephtWise Conv2D, no weigths-pruning ------> 63.8%, 1162.1 kB 

-3rd model: Log-Mel preprocessing args(64 bin, lower_freq = 20, upper_freq = 4000) with callbacks, CNN without DephtWise Conv2D, no weigths-pruning ------> 77.4%, 1162.1 kB 

-4th model: Log-Mel preprocessing args(40 bin, lower_freq = 30, upper_freq = 6000) with callbacks, CNN without DephtWise Conv2D, no weigths-pruning ------> 86.6%, 1162.1 kB 

-5th model: Log-Mel preprocessing args(40 bin, lower_freq = 30, upper_freq = 6000, batch_size = 20, epochs = 30) with callbacks(lr from 0.01 to 0.0001), CNN without DephtWise Conv2D, no weigths-pruning ------> 95%, 1162.1 kB

-6th model: Log-Mel preprocessing args(40 bin, length = 16ms, step = 8ms, lower_freq = 20, upper_freq = 4000, batch_size = 20, epochs = 20) with callbacks(lr from 0.01 to 0.0001), CNN without DephtWise Conv2D, no weigths-pruning ------> 94%, 1162.1 kB
