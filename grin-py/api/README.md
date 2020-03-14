# Grin-Pool API

#### Table Of Contents
* [grin](#grin)
  * [blocks](#grinblocks)
  * [stats](#grinstats)
* [pool](#pool)
  * [blocks](#poolblocks)
  * [block count](#poolblockcount)
  * [stats](#poolstats)
  * [share count](#poolsharecount)
  * [user accounts](#poolusers)
    * [create account](#createaccount)
    * [get api token](#getapitoken)
  * [estimates](#poolestimates)
* [worker](#worker)
  * [stats](#workerstats)
  * [shares](#workershares)
  * [blocks](#workerblocks)
  * [payments](#workerpayments)
  * [settings](#workersettings)
  * [estimates](#workerestimates)
* [payment request](#paymentrequest)
  * [offline](#offlinepayment)
  * [online](#onlinepayment)



<a name="grin"></a>
## Grin:

<a name="grinblocks"/></a>
### Blocks:
```/grin/block```

    Get the latest block

```/grin/block/<string:fields>```
    
    Get the latest block
    Filter out all but specified fields

```/grin/block/<int:height>```

    Get a single block at specified height
    Specify height = 0 to start at the ‘latest’ height 

```/grin/block/<int:height>/<string:fields>```

    Get a single block at specified height 
    Specify height = 0 to start at the ‘latest’ height 
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


<a name="grinstats"/></a>
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
    


<a name="pool"/></a>
## Pool:


<a name="poolblocks"/></a>
### Blocks:

```/pool/block```

    Get the latest block mined by pool

```/pool/block/<string:fields>```
    
    Get the latest pool block
    Filter all but specified fields

```/pool/block/<int:height>```

    Get a single pool block at specified height
    Will return null if there is no pool-found block at that height

```/pool/block/<int:height>/<string:fields>```
        
    Get a single pool block at specified height 
    Will return null if there is no pool-found block at that height
    Filter all but specified fields

```/pool/blocks/<int:height>,<int:range>```

    Get a range of pool blocks
    Will return None if there are no pool-found block in that range


```/pool/blocks/<int:height>,<int:range>/<string:fields>```

    Get a range of pool blocks
    Will return None if there are no pool-found block in that range
    Filter all but specified fields


<a name="poolblockcount"/></a>
### Block Counts:


```/pool/blocks/count```

    Get the number of pool blocks found by the pool


```/pool/blocks/count/<int:height>```

    Get the number of pool blocks found up to height



<a name="poolstats"/></a>
### Stats:

```/pool/stat```

    Get pool stats for the latest block 

```/pool/stat/<string:fields>```

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



<a name="poolsharecount"/></a>
### Share Counts:

```/pool/share/count```

    Get the number of shares submitted to the pool by all workers:
      count = for this block
      total = for all blocks

```/pool/share/count/<int:height>```

    Get the number of shares submitted to the pool by all workers:
      count = for this block
      total = for all blocks up to height

```/pool/share/counts/<int:height>,<int:range>```

    Get the total number of shares submitted to the pool by all workers for a range of blocks:
      count: for each block
      total = for all blocks up to blocks height



<a name="poolusers"/></a>
### User Accounts:

<a name="createaccount"/></a>
#### Create a new account:

```/pool/users```

    Create a new user account given username and password as FORM data
    POST method
    Form Data required:  "username=<string>", and "password=<string>"

<a name="getapitoken"/></a>
#### Get an API token:
##### Requires ```basicauth```

```/pool/users```

    Get an API token (that expires) for user
    GET method

<a name="poolestimates"/></a>
#### Get daily earnings estimate:

```/pool/estimate/dailyearning```

    Get the expected daily earning estimate for all current POW sizes for 1 GPS at latest network height

```/pool/estimate/dailyearning/<int:height>```

    Get the expected daily earning estimate for all current POW sizes for 1 GPS at specified network height.
    Specify height=0 for latest network height.

```/pool/estimate/dailyearning/<int:height>/<int:gps>```

    Get the expected daily earning estimate for all current POW sizes for specified GPS at specified network height.
    Specify height=0 for the latest network height.



<a name="worker"/></a>
## Worker:

<a name="workerstats"/></a>
### Stats:

#### For all active Workers:
#### Requires ```basicauth```

```/workers/stat```

    Get the latest worker stats the pool has, for all active workers

```/workers/stat/<string:fields>```

    Get the latest worker stats the pool has, for all active workers
    Filter all but specified fields

```/workers/stat/<int:height>```

    Get worker stats for the block at specified height for all active workers
    Specify height = 0 to get stats from the ‘latest’ block height

```/workers/stat/<int:height>/<string:fields>```
        
    Get worker stats for the block at specified height for all active workers
    Specify height = 0 to get stats from the ‘latest’ block height
    Filter all but specified fields

```/workers/stats/<int:height>,<int:range>```

    Get worker stats from a range of pool blocks for all active workers
    Starting at ‘height’ and returning the previous ‘range’ of blocks
    Specify height = 0 to start at the ‘latest’ height 

```/workers/stats/<int:height>,<int:range>/<string:fields>```

    Get worker stats from a range of pool blocks for all active workers
    Starting at ‘height’ and returning the previous ‘range’ of blocks
    Specify height = 0 to start at the ‘latest’ height 
    Filter all but specified fields


#### For one specific worker:
#### Requires ```basicauth```

```/worker/stat/<int:id>```

    Get most recent worker stat for specified worker

```/worker/stat/<int:id>/<string:fields>```

    Get most recent worker stat for specified worker
    Filter all but specified fields

```/worker/stat/<int:id>/<int:height>```

    Get worker stat for the block at the specified height for specified worker

```/worker/stat/<int:id>/<int:height>/<string:fields>```

    Get worker stat for the block at the specified height for specified worker
    Specify height = 0 to start at the ‘latest’ height 
    Filter all but specified fields

```/worker/stats/<int:id>/<int:height>,<int:range>```

    Get worker stats for a range of blocks for specified worker
    Starting at ‘height’ and returning the previous ‘range’ of blocks
    Specify height = 0 to start at the ‘latest’ height 

```/worker/stats/<int:id>/<int:height>,<int:range>/<string:fields>```

    Get worker stats for a range of blocks for specified worker
    Starting at ‘height’ and returning the previous ‘range’ of blocks
    Specify height = 0 to start at the ‘latest’ height 
    Filter all but specified fields



<a name="workershares"/></a>
### Shares:

#### For all active Workers:
#### Requires ```basicauth```

```/workers/shares```

    Get worker shares data for the latest block height for all active workers

```/workers/shares/<string:fields>```

    Get worker shares data for the latest block height for all active workers
    Filter all but specified fields

```/workers/shares/<int:height>```

    Get worker shares data for the block at specified height for all active workers
    Specify height = 0 to get shares data from the latest block height

```/workers/shares/<int:height>/<string:fields>```

    Get worker shares data for the block at specified height for all active workers
    Specify height = 0 to get shares data from the latest block height
    Filter all but specified fields

```/workers/shares/<int:height>,<int:range>```

    Get worker shares data from a range of pool blocks for all active workers
    Starting at 'height' and returning the previous 'range' of blocks
    Specify height = 0 to start at the latest height

```/workers/shares/<int:height>,<int:range>/<string:fields>```

    Get worker shares data from a range of pool blocks for all active workers
    Starting at 'height' and returning the previous 'range' of blocks
    Specify height = 0 to start at the latest height
    Filter all but specified fields


#### For one specific worker:
#### Requires ```basicauth```

```/worker/shares/<int:id>/<int:height>```

    Get worker shares data for the block at the specified height for specified worker

```/worker/shares/<int:id>/<int:height>/<string:fields>```

    Get worker shares data for the block at the specified height for specified worker
    Starting at 'height' and returning the previous 'range' of blocks
    Specify height = 0 to start at the latest height
    Filter all but specified fields

```/worker/shares/<int:id>/<int:height>,<int:range>```

    Get worker shares data for a range of blocks for specified worker
    Starting at 'height' and returning the previous 'range' of blocks
    Specify height = 0 to start at the latest height

```/worker/shares/<int:id>/<int:height>,<int:range>/<string:fields>```

    Get worker shares data for a range of blocks for specified worker
    Starting at 'height' and returning the previous 'range' of blocks
    Specify height = 0 to start at the latest height
    Filter all but specified fields


<a name="workerblocks"/></a>
### Blocks:
#### Requires ```basicauth```

```/worker/block/<int:id>```

    Get the latest block mined by user id

```/pool/block/<int:id>/<string:fields>```
    
    Get the latest block mined by user id
    Filter all but specified fields

```/pool/block/<int:id>/<int:height>```

    Get a single block found by user id at specified height
    Will return null if there is no block found by user id at that height

```/pool/block/<int:id>/<int:height>/<string:fields>```
        
    Get a single block found by user id at specified height
    Will return null if there is no block found by user id at that height
    Filter all but specified fields

```/pool/blocks/<int:id>/<int:height>,<int:range>```

    Get a range of blocks found by user id within height and range
    Will return None if there are no blocks found by user id in that range


```/pool/blocks/<int:id>/<int:height>,<int:range>/<string:fields>```

    Get a range of blocks found by user id within height and range
    Will return None if there are no blocks found by user id in that range
    Filter all but specified fields


<a name="workerpayments"/></a>
### User Balance and Payments:

#### Get user balance and payment method data:
#### Requires ```basicauth```

```/worker/utxo/<int:id>```

    Get the workers outstanding balance and payment method data


<a name="workersettings"/></a>
### Set user payment method:
#### Requires ```basicauth```

```/worker/utxo/<int:id>/<string:field>/<string:value>```

   Set the workers "address", or "method" values
   POST method


<a name="workerpayments"/></a>
#### Get user payment data:
#### Requires ```basicauth```

```/worker/payment/<int:id>```

    Get the most recent payment record for a worker

```/worker/payment/<int:id>/<string:fields>```

    Get the most recent payment record for a worker
    Filter all but specified fields

```/worker/payments/<int:id>/<int:range>```

    Get the range of most recent payment records for a worker

```/worker/payments/<int:id>/<int:range>/<string:fields>```

    Get the range of most recent payment records for a worker
    Filter all but specified fields


<a name="workerestimates"/></a>
#### Get user earnings estimates:
#### Requires ```basicauth```

```/worker/estimate/payment/<int:id>```

    Get the current immature balance estimate for worker with specified id.

```/worker/estimate/payment/<int:id>/<int:height>```

    Get the block reward estimate for worker with specified id, for block at specified height

```/worker/estimate/payment/<int:id>/<int:height>,range```

    Get the block reward estimates for worker with specified id, for a range of blocks at specified height

```/worker/estimate/payment/<int:id>/next```

    Get the block reward estimate for worker with specified id, for the next block found by the pool



<a name="paymentrequest"/></a>
#### Request Payments - Both online and offline
#### Requires ```basicauth```

<a name="offlinepayment"/></a>
```/pool/payment/<string:function>/<int:id>```

    Initiate an Offline Payout for user id
    Available functions are:
    * get_tx_slate - Request an unsigned tx slate
    * submit_tx_slate - Submit a signed tx slate
    * payout_script - Get a scipt to help automate payouts
    POST method

<a name="onlinepayment"/></a>
```/pool/payment/<string:function>/<int:id>/<string:address>```

    Initiate an Online Payout for user id to address
    Available methds are:
    * http - HTTP Wallet-To-Wallet tx
    * grinbox - Coming Soon (tm)
    * keybase - Coming Soon (tm)

