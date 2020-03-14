import {BaseEntity,Column,Entity,Index,JoinColumn,JoinTable,ManyToMany,ManyToOne,OneToMany,OneToOne,PrimaryColumn,PrimaryGeneratedColumn,RelationId} from "typeorm";
import {users} from "./users";
import {gps} from "./gps";


@Entity("worker_stats",{schema:"pool"})
@Index("user_id",["user_",])
@Index("ix_worker_stats_height",["height",])
@Index("ix_worker_stats_timestamp",["timestamp",])
@Index("ix_worker_stats_dirty",["dirty",])
export class worker_stats {

    @PrimaryGeneratedColumn({
        type:"int", 
        name:"id"
        })
    id:number;
        

    @Column("datetime",{ 
        nullable:false,
        name:"timestamp"
        })
    timestamp:Date;
        

    @Column("bigint",{ 
        nullable:false,
        name:"height"
        })
    height:string;
        

    @Column("int",{ 
        nullable:true,
        name:"valid_shares"
        })
    valid_shares:number | null;
        

    @Column("int",{ 
        nullable:true,
        name:"invalid_shares"
        })
    invalid_shares:number | null;
        

    @Column("int",{ 
        nullable:true,
        name:"stale_shares"
        })
    stale_shares:number | null;
        

    @Column("bigint",{ 
        nullable:true,
        name:"total_valid_shares"
        })
    total_valid_shares:string | null;
        

    @Column("bigint",{ 
        nullable:true,
        name:"total_invalid_shares"
        })
    total_invalid_shares:string | null;
        

    @Column("bigint",{ 
        nullable:true,
        name:"total_stale_shares"
        })
    total_stale_shares:string | null;
        

    @Column("tinyint",{ 
        nullable:true,
        width:1,
        name:"dirty"
        })
    dirty:boolean | null;
        

   
    @ManyToOne(type=>users, users=>users.worker_statss,{ onDelete: 'RESTRICT',onUpdate: 'RESTRICT' })
    @JoinColumn({ name:'user_id'})
    user_:users | null;


   
    @OneToMany(type=>gps, gps=>gps.worker_stats_,{ onDelete: 'RESTRICT' ,onUpdate: 'RESTRICT' })
    gpss:gps[];
    
}
