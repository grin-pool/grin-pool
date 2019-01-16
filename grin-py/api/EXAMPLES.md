# Grin-Pool API Examples

## Grin:

### Blocks:

#### ```GET``` ```/grin/block```

~~
curl $APIURL/grin/block

{
    "lock_height": 72400,
    "range_proof_root": "3d755971d2bc486e229b94be9e3b6544da1b5494df10cf2f0775c3381c8e25fe",
    "timestamp": 1544221296.0,
    "version": 1,
    "hash": "0209393a38434f53134a162e3d52d9463441b26d8cc980ba3c38b6c5269d7ddb",
    "output_root": "b8d9d8313335bf6369ad9ac2d48212b2d6f828a65f72fbdd1abe0d4cde7b578c",
    "previous": "06c9ce087e3765997c4636f9fcbad8730936b67aa918aed5162bd561a2ca65b8",
    "fee": 0,
    "num_kernels": 1,
    "nonce": "15704385892378057869",
    "num_outputs": 1,
    "num_inputs": 0,
    "state": "new",
    "height": 72400,
    "secondary_scaling": 708,
    "edge_bits": 29,
    "total_difficulty": 4861690246,
    "kernel_root": "ea5b41cfce57a8f8d8c6e2362e961a5b4c73576cb7410afd9adcfb1e22cc5a6b",
    "total_kernel_offset": "0bd3f606b76707455a39eb00e369cc49cc410f0145db5494b51b18a2ba5ec679"
}

~~

#### ```GET``` ```/grin/block/<string:fields>```

~~
curl $APIURL/grin/block/hash,height

curl $APIURL/grin/block/hash,height
{
    "hash": "01224cc707d3c61e83cd72b5acc286a7047e719295940cec304fac6efa876c0c",
    "height": 72439
}
~~

