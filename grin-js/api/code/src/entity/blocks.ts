import {BaseEntity,Column,Entity,Index,JoinColumn,JoinTable,ManyToMany,ManyToOne,OneToMany,OneToOne,PrimaryColumn,PrimaryGeneratedColumn,RelationId} from "typeorm";


@Entity("blocks",{schema:"pool"})
@Index("ix_blocks_height",["height",])
@Index("ix_blocks_timestamp",["timestamp",])
export class blocks {

    @Column("bigint",{ 
        nullable:false,
        primary:true,
        name:"height"
        })
    height:string;
        

    @Column("varchar",{ 
        nullable:true,
        length:64,
        name:"hash"
        })
    hash:string | null;
        

    @Column("smallint",{ 
        nullable:true,
        name:"version"
        })
    version:number | null;
        

    @Column("varchar",{ 
        nullable:true,
        length:64,
        name:"previous"
        })
    previous:string | null;
        

    @Column("datetime",{ 
        nullable:false,
        name:"timestamp"
        })
    timestamp:Date;
        

    @Column("varchar",{ 
        nullable:true,
        length:64,
        name:"output_root"
        })
    output_root:string | null;
        

    @Column("varchar",{ 
        nullable:true,
        length:64,
        name:"range_proof_root"
        })
    range_proof_root:string | null;
        

    @Column("varchar",{ 
        nullable:true,
        length:64,
        name:"kernel_root"
        })
    kernel_root:string | null;
        

    @Column("varchar",{ 
        nullable:false,
        length:20,
        name:"nonce"
        })
    nonce:string;
        

    @Column("smallint",{ 
        nullable:true,
        name:"edge_bits"
        })
    edge_bits:number | null;
        

    @Column("bigint",{ 
        nullable:true,
        name:"total_difficulty"
        })
    total_difficulty:string | null;
        

    @Column("bigint",{ 
        nullable:true,
        name:"secondary_scaling"
        })
    secondary_scaling:string | null;
        

    @Column("int",{ 
        nullable:true,
        name:"num_inputs"
        })
    num_inputs:number | null;
        

    @Column("int",{ 
        nullable:true,
        name:"num_outputs"
        })
    num_outputs:number | null;
        

    @Column("int",{ 
        nullable:true,
        name:"num_kernels"
        })
    num_kernels:number | null;
        

    @Column("bigint",{ 
        nullable:true,
        name:"fee"
        })
    fee:string | null;
        

    @Column("bigint",{ 
        nullable:true,
        name:"lock_height"
        })
    lock_height:string | null;
        

    @Column("varchar",{ 
        nullable:true,
        length:64,
        name:"total_kernel_offset"
        })
    total_kernel_offset:string | null;
        

    @Column("varchar",{ 
        nullable:true,
        length:64,
        name:"state"
        })
    state:string | null;
        
}
