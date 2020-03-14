import {BaseEntity,Column,Entity,Index,JoinColumn,JoinTable,ManyToMany,ManyToOne,OneToMany,OneToOne,PrimaryColumn,PrimaryGeneratedColumn,RelationId} from "typeorm";
import {pool_blocks} from "./pool_blocks";
import {pool_payment} from "./pool_payment";
import {pool_utxo} from "./pool_utxo";
import {worker_shares} from "./worker_shares";
import {worker_stats} from "./worker_stats";


@Entity("users",{schema:"pool"})
@Index("ix_users_username",["username",],{unique:true})
export class users {

    @PrimaryGeneratedColumn({
        type:"int", 
        name:"id"
        })
    id:number;
        

    @Column("varchar",{ 
        nullable:true,
        unique: true,
        length:64,
        name:"username"
        })
    username:string | null;
        

    @Column("varchar",{ 
        nullable:true,
        length:128,
        name:"password_hash"
        })
    password_hash:string | null;
        

    @Column("varchar",{ 
        nullable:true,
        name:"email"
        })
    email:string | null;
        

    @Column("text",{ 
        nullable:true,
        name:"settings"
        })
    settings:string | null;
        

    @Column("varchar",{ 
        nullable:true,
        name:"extra1"
        })
    extra1:string | null;
        

    @Column("varchar",{ 
        nullable:true,
        name:"extra2"
        })
    extra2:string | null;
        

    @Column("varchar",{ 
        nullable:true,
        name:"extra3"
        })
    extra3:string | null;
        

   
    @OneToMany(type=>pool_blocks, pool_blocks=>pool_blocks.found_by,{ onDelete: 'RESTRICT' ,onUpdate: 'RESTRICT' })
    pool_blockss:pool_blocks[];
    

   
    @OneToMany(type=>pool_payment, pool_payment=>pool_payment.user_,{ onDelete: 'RESTRICT' ,onUpdate: 'RESTRICT' })
    pool_payments:pool_payment[];
    

   
    @OneToMany(type=>pool_utxo, pool_utxo=>pool_utxo.user_,{ onDelete: 'RESTRICT' ,onUpdate: 'RESTRICT' })
    pool_utxos:pool_utxo[];
    

   
    @OneToMany(type=>worker_shares, worker_shares=>worker_shares.user_,{ onDelete: 'RESTRICT' ,onUpdate: 'RESTRICT' })
    worker_sharess:worker_shares[];
    

   
    @OneToMany(type=>worker_stats, worker_stats=>worker_stats.user_,{ onDelete: 'RESTRICT' ,onUpdate: 'RESTRICT' })
    worker_statss:worker_stats[];
    
}
