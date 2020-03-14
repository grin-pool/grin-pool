import {BaseEntity,Column,Entity,Index,JoinColumn,JoinTable,ManyToMany,ManyToOne,OneToMany,OneToOne,PrimaryColumn,PrimaryGeneratedColumn,RelationId} from "typeorm";
import {gps} from "./gps";


@Entity("pool_stats",{schema:"pool"})
@Index("ix_pool_stats_dirty",["dirty",])
@Index("ix_pool_stats_timestamp",["timestamp",])
@Index("ix_pool_stats_height",["height",])
export class pool_stats {

    @Column("bigint",{ 
        nullable:false,
        primary:true,
        name:"height"
        })
    height:string;
        

    @Column("datetime",{ 
        nullable:false,
        name:"timestamp"
        })
    timestamp:Date;
        

    @Column("int",{ 
        nullable:true,
        name:"active_miners"
        })
    active_miners:number | null;
        

    @Column("int",{ 
        nullable:true,
        name:"shares_processed"
        })
    shares_processed:number | null;
        

    @Column("int",{ 
        nullable:true,
        name:"total_blocks_found"
        })
    total_blocks_found:number | null;
        

    @Column("bigint",{ 
        nullable:true,
        name:"total_shares_processed"
        })
    total_shares_processed:string | null;
        

    @Column("tinyint",{ 
        nullable:true,
        width:1,
        name:"dirty"
        })
    dirty:boolean | null;
        

   
    @OneToMany(type=>gps, gps=>gps.pool_stats_,{ onDelete: 'RESTRICT' ,onUpdate: 'RESTRICT' })
    gpss:gps[];
    
}
