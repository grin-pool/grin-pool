import {BaseEntity,Column,Entity,Index,JoinColumn,JoinTable,ManyToMany,ManyToOne,OneToMany,OneToOne,PrimaryColumn,PrimaryGeneratedColumn,RelationId} from "typeorm";
import {users} from "./users";


@Entity("pool_utxo",{schema:"pool"})
@Index("user_id",["user_",])
@Index("ix_pool_utxo_id",["id",])
export class pool_utxo {

    @PrimaryGeneratedColumn({
        type:"int", 
        name:"id"
        })
    id:number;
        

    @Column("varchar",{ 
        nullable:true,
        length:1024,
        name:"address"
        })
    address:string | null;
        

    @Column("varchar",{ 
        nullable:true,
        length:64,
        name:"method"
        })
    method:string | null;
        

    @Column("tinyint",{ 
        nullable:true,
        width:1,
        name:"locked"
        })
    locked:boolean | null;
        

    @Column("bigint",{ 
        nullable:true,
        name:"amount"
        })
    amount:string | null;
        

    @Column("int",{ 
        nullable:true,
        name:"failure_count"
        })
    failure_count:number | null;
        

    @Column("datetime",{ 
        nullable:true,
        name:"last_try"
        })
    last_try:Date | null;
        

    @Column("datetime",{ 
        nullable:true,
        name:"last_success"
        })
    last_success:Date | null;
        

    @Column("bigint",{ 
        nullable:true,
        name:"total_amount"
        })
    total_amount:string | null;
        

   
    @ManyToOne(type=>users, users=>users.pool_utxos,{ onDelete: 'RESTRICT',onUpdate: 'RESTRICT' })
    @JoinColumn({ name:'user_id'})
    user_:users | null;

}
