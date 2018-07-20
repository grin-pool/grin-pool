### blocks
```
A record of blocks as seen by the pools grin node responsible for building blocks.
Blocks are added to the db as they are accepted by the grin node.
blockWatcher.py polls the grin node API port for new blocks.
Records have initial "state" of "new".
blockValidator.py checks the record of each block against the grin-node after some amount of time passes.
Blocks that dont match have "state" changed to "orphan".
NOTE that the orhpan block data is *not* updated in our database.
```

### pool_shares
```
A record of shares processed and accepted by the pool.
shareWatcher.py watches the POOL_LOG for share messages and adds them to our database.
These records contain the worker logins which are needed for payout.
These records have not been validated for difficulty yet. The pool does not verify difficulty.
These records contain "worker_difficulty".
They also have fields:	"validated" - initially false
			"is_valid" - intially NULL
			"invalid_reason" - intially NULL
shareValidator.py validates pool_share:
	Check if a matching grin_share exists.  If not, this share was rejected and is invalid
	Check grin_share.actual_difficulty >= pool_share.worker_difficulty or mark invalid
	Check nonce and timestamp against grin_share for added sanity
```

### grin_shares
```
A record of shares processed and accepted by the grin node.
shareWatcher.py watches GRIN_LOG for share messages.
These records contain the "actual_difficulty" and "net_difficulty".
Note:  Some pool_shares will be rejected by grin-node and get logged as failures rather than grin_shares.
Also has field:	"is_solution" (not sure why)
Nothing needs to be verified here.
```

### pool_blocks
```
A record of all blocks found by the pool.
shareWatcher.py watches GRIN_LOG for accepted shares with difficulty > net difficulty.
Has a field:	"state" - intially "new"
Has a field:	"found_by" - this is the pool instnace that found the block - need to look in pool_shares for worker who found it.
poolblockUnlocker.py enforces the LOCKTIME for new coinbase rewards
poolblockUnlocker.py validates against (grin node or blocks record) for orphan condition
Orphans are marked, or blocks are unlocked.
```

### pool_utxo <--- these are our user records.  
```
A record of each pending payout (one per unique miner payout address)
makePayouts.py gets the list of pool_utxo records with value greater than threshold and attepmts to make a payment.
    * Bonus: Do all payouts in a single tx ?
    * updates pool_utxo with new total, timestamp of last payout, number of failed payout attempts
```




# Some idea of the modules involved and what each does:
```
api - Used by Front-End UI to get data from the database
pool - Where the miners connect to:
        * Run as a service
        * connects to grin core stratum server and accepts jobs
        * Accepts worker connections and sends jobs to workers
        * Accepts solution shares from workers and stores them in the database and log file)
        * Handles worker difficulty calculations and adjustments
blockWatcher - Watches the blockchain for new blocks
        * Run as a service
        * Request chain height from grin core every x seconds.
        * If the height increased request each block from grin core.
        * Adds them to the database.  This keeps a record of each block *as we see it* (before any chain reorgs).
solutionWatcher - Watches grin log for solutions
        * Run as a service (tailing grin log)
        * adds our blocks to the database
        * Mark as new
shareWatcher - Watches pool log for worker shares
        * Run as a service (tailing pool log)
        * Adds shares to the database
blockValidater - Verify our mysql chain against the grin network.
        * Run as a scheduled job
        * Add missing blocks.
        * Mark orphan blocks.
blockUnlocker - Checks blocks found by the pool to see if they are ready to be unlocked and made available for payout.
        * Run as scheduled job
        * Check blocks found by our pool
        * if they are old enough and not orphan
        * Mark as unlocked
payout - pay out for unlocked blocks
        * Run as scheduled job
        * calculates payouts based on shares contributed
        * makes payments for "payable" pool_blocks
        * Mark as paid
janitor - Cleans up the database
        * Run as scheduled job
        * Delete records of old shares
auditor - Check that the numbers add up
        * Run as a scheduled job
        * Verify user shares = payouts
        * Verify wallet in = wallet out for each block
        * Verify more
        * Marks pool_blocks as payable
```
