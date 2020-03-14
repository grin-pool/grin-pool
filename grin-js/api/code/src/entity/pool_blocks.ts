import {BaseEntity,Column,Entity,Index,JoinColumn,JoinTable,ManyToMany,ManyToOne,OneToMany,OneToOne,PrimaryColumn,PrimaryGeneratedColumn,RelationId} from "typeorm";
import {users} from "./users";


@Entity("pool_blocks",{schema:"pool"})
@Index("found_by",["found_by",])
@Index("ix_pool_blocks_timestamp",["timestamp",])
@Index("ix_pool_blocks_height",["height",])
export class pool_blocks {

    @PrimaryGeneratedColumn({
        type:"bigint", 
        name:"height"
        })
    height:string;
        

    @Column("varchar",{ 
        nullable:true,
        length:64,
        name:"hash"
        })
    hash:string | null;
        

    @Column("varchar",{ 
        nullable:false,
        length:20,
        name:"nonce"
        })
    nonce:string;
        

    @Column("bigint",{ 
        nullable:true,
        name:"actual_difficulty"
        })
    actual_difficulty:string | null;
        

    @Column("bigint",{ 
        nullable:true,
        name:"net_difficulty"
        })
    net_difficulty:string | null;
        

    @Column("datetime",{ 
        nullable:false,
        name:"timestamp"
        })
    timestamp:Date;
        

    @Column("varchar",{ 
        nullable:true,
        length:20,
        name:"state"
        })
    state:string | null;
        

   
    @ManyToOne(type=>users, users=>users.pool_blockss,{ onDelete: 'RESTRICT',onUpdate: 'RESTRICT' })
    @JoinColumn({ name:'found_by'})
    found_by:users | null;

}
