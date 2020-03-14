import {BaseEntity,Column,Entity,Index,JoinColumn,JoinTable,ManyToMany,ManyToOne,OneToMany,OneToOne,PrimaryColumn,PrimaryGeneratedColumn,RelationId} from "typeorm";
import {users} from "./users";


@Entity("pool_payment",{schema:"pool"})
@Index("user_id",["user_",])
@Index("ix_pool_payment_timestamp",["timestamp",])
@Index("ix_pool_payment_height",["height",])
export class pool_payment {

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
        

    @Column("varchar",{ 
        nullable:true,
        length:1024,
        name:"address"
        })
    address:string | null;
        

    @Column("bigint",{ 
        nullable:true,
        name:"amount"
        })
    amount:string | null;
        

    @Column("varchar",{ 
        nullable:true,
        length:64,
        name:"method"
        })
    method:string | null;
        

    @Column("bigint",{ 
        nullable:true,
        name:"fee"
        })
    fee:string | null;
        

    @Column("int",{ 
        nullable:true,
        name:"failure_count"
        })
    failure_count:number | null;
        

    @Column("varchar",{ 
        nullable:true,
        length:16,
        name:"invoked_by"
        })
    invoked_by:string | null;
        

    @Column("varchar",{ 
        nullable:true,
        length:16,
        name:"state"
        })
    state:string | null;
        

    @Column("mediumtext",{ 
        nullable:true,
        name:"tx_data"
        })
    tx_data:string | null;
        

   
    @ManyToOne(type=>users, users=>users.pool_payments,{ onDelete: 'RESTRICT',onUpdate: 'RESTRICT' })
    @JoinColumn({ name:'user_id'})
    user_:users | null;

}
