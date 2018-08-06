# Grin-Pool API


## Grin:

### Blocks:
```/grin/block```

    Get the latest block

```/grin/block/<string:fields>```
    
    Get the latest block
    Filter out all but specified fields

```/grin/block/<int:height>```

    Get a single block at specified height

```/grin/block/<int:height>/<string:fields>```

    Get a single block at specified height 
    Filter out all but specified fields

```/grin/blocks/<int:height>,<int:range>```

    Get a range of blocks
    Starting at ‘height’ and returning the previous ‘range’ of blocks
    Specify height = 0 to start at the ‘latest’ height 

```/grin/blocks/<int:height>,<int:range>/<string:fields>```

    Get a range of blocks
    Filter out all but specified fields
    Starting at ‘height’ and returning the previous ‘range’ of blocks
    Specify height = 0 to start at the ‘latest’ height 


### Stats:

```/grin/stat```

    Get grin stats for the latest block

```/grin/stat/<string:fields>```

    Get grin stats for the latest block 
    Filter out all but specified fields

```/grin/stat/<int:height>```

    Get grin stats for the block at specified height

```/grin/stat/<int:height>/<string:fields>```

    Get grin stats for the block at specified height
    Filter out all but specified fields

```/grin/stats/<int:height>,<int:range>```

    Get grin stats for a range of blocks

```/grin/stats/<int:height>,<int:range>/<string:fields>```

    Get grin stats for a range of blocks 
    Filter out all but specified fields
    


## Pool:


### Blocks:

```/pool/block```

    Get the latest pool block

```/pool/block/<string:fields>```
    
    Get the latest pool block
    Filter all but specified fields

```/pool/block/<int:height>```

    Get a single pool block at specified height
    Will return None if there is no pool-found block at that height

```/pool/block/<int:height>/count```

    Get the number of pool blocks found up to height

```/pool/block/<int:height>/<string:fields>```
        
    Get a single pool block at specified height 
    Will return None if there is no pool-found block at that height
    Filter all but specified fields

```/pool/blocks/<int:height>,<int:range>```

    Get a range of pool blocks
    Will return None if there are no pool-found block in that range


```/pool/blocks/<int:height>,<int:range>/<string:fields>```

    Get a range of pool blocks
    Will return None if there are no pool-found block in that range
    Filter all but specified fields

### Stats:

```/pool/stat```

    Get pool stats for the latest block 

```/pool/stat/<int:height>```

    Get pool stats for the latest block
    Filter out all but specified fields
    
```/pool/stat/<int:height>```

    Get pool stats for a single block at specified height
    
```/pool/stat/<int:height>/<string:fields>```

    Get pool stats for a single block at specified height 
    Filter all but specified fields

```/pool/stats/<int:height>,<int:range>```

    Get pool stats for a range of blocks

```/pool/stats/<int:height>,<int:range>/<string:fields>```

    Get pool stats for a range of blocks 
    Filter all but specified fields



## Worker:

### Share Count:

```/worker/shares/count```
    
    Get the count of all shares submitted to the pool
        
 ```/worker/shares/<int:height>/count```
    
    Get the count of all shares submitted to the pool for the block at specified height

```/worker/shares/<int:height>,<int:range>/count```

    Get the count of all shares submitted to the pool within specified block range
    Starting at ‘height’ and returning the previous ‘range’ of blocks
    Specify height = 0 to start at the ‘latest’ height
    Specify range = 0 to get count of shares submitted for all blocks up to height

```/worker/shares/<string:id>/count```
    
    Get the count of shares for the latest block from worker id

```/worker/shares/<string:id>/<int:height>/count```
    
    Get the count of shares for the block at height from worker id
    Specify height = 0 to get shares from the ‘latest’ height

```/worker/shares/<string:id>/<int:height>,<int:range>/count```

    Get the count of shares submitted to the pool within specified block range by worker id
    Starting at ‘height’ and returning the previous ‘range’ of blocks
    Specify height = 0 to get shares from the ‘latest’ height
    Specify range = 0 to get count of shares submitted for all blocks up to height

### Shares:

```/worker/shares/<string:id>```

    Get all shares from all workers for the latest block

```/worker/shares/<string:id>/<string:fields>```

    Get all shares for the latest block from worker id
    Filter all but specified fields

```/worker/shares/<string:id>/<int:height>```

    Get all shares from the block at height from worker id
    Specify height = 0 to get shares from the ‘latest’ height

```/worker/shares/<string:id>/<int:height>/<string:fields>```

    Get all shares from the block at height from worker id
    Filter all but specified fields
    Specify height = 0 to get shares from the ‘latest’ height

```/worker/shares/<string:id>/<int:height>,<int:range>```

    Get all shares from a range of pool blocks from worker id
    Starting at ‘height’ and returning the previous ‘range’ of blocks
    Specify height = 0 to start at the ‘latest’ height 

```/worker/shares/<string:id>/<int:height>,<int:range>/<string:fields>```

    Get all shares from a range of pool blocks from worker id
    Starting at ‘height’ and returning the previous ‘range’ of blocks
    Specify height = 0 to start at the ‘latest’ height 
    Filter all but specified fields

### Stats:

#### For all active Workers:

```/worker/stats/<int:height>```

    Get worker stats for the block at specified height for all active workers
    Specify height = 0 to get stats from the ‘latest’ block height

```/worker/stats/<int:height>/<string:fields>```
        
    Get worker stats for the block at specified height for all active workers
    Specify height = 0 to get stats from the ‘latest’ block height
    Filter all but specified fields

```/worker/stats/<int:height>,<int:range>```

    Get worker stats from a range of pool blocks for all active workers
    Starting at ‘height’ and returning the previous ‘range’ of blocks
    Specify height = 0 to start at the ‘latest’ height 

```/worker/stats/<int:height>,<int:range>/<string:fields>```

    Get worker stats from a range of pool blocks for all active workers
    Starting at ‘height’ and returning the previous ‘range’ of blocks
    Specify height = 0 to start at the ‘latest’ height 
    Filter all but specified fields

#### For one specific worker:

```/worker/stats/<string:id>/<int:height>```

    Get worker stats for the block at the specified height for specified worker

```/worker/stats/<string:id>/<int:height>/<string:fields>```

    Get worker stats for the block at the specified height for specified worker
    Starting at ‘height’ and returning the previous ‘range’ of blocks
    Specify height = 0 to start at the ‘latest’ height 
    Filter all but specified fields

```/worker/stats/<string:id>/<int:height>,<int:range>```

    Get worker stats for a range of blocks for specified worker
    Starting at ‘height’ and returning the previous ‘range’ of blocks
    Specify height = 0 to start at the ‘latest’ height 

```/worker/stats/<string:id>/<int:height>,<int:range>/<string:fields>```

    Get worker stats for a range of blocks for specified worker
    Starting at ‘height’ and returning the previous ‘range’ of blocks
    Specify height = 0 to start at the ‘latest’ height 
    Filter all but specified fields



## Examples:

Q: How do I get the grin network current graph rate?
A: ```curl grin-pool.us:13423/grin/stat/gps```
Ex: ```{ "gps": 9.73408 }```

Q: How do I get timestamp of the last grin block found?
A: ```curl grin-pool.us:13423/grin/block/timestamp```
Ex: ```{ "timestamp": 1533279887.0 }```

Q: How do I get data needed to graph the grin network graph rate over the past 60 blocks?
A: ```curl grin-pool.us:13423/grin/stats/0,60/gps```

Q: How do I get the pools current graph rate?
A: ```curl grin-pool.us:13423/pool/stat/gps```

Xxx add more
