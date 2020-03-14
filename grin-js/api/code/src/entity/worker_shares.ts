import {BaseEntity,Column,Entity,Index,JoinColumn,JoinTable,ManyToMany,ManyToOne,OneToMany,OneToOne,PrimaryColumn,PrimaryGeneratedColumn,RelationId} from "typeorm";
import {users} from "./users";
import {shares} from "./shares";


@Entity("worker_shares",{schema:"pool"})
@Index("user_id",["user_",])
@Index("ix_worker_shares_timestamp",["timestamp",])
export class worker_shares {

    @PrimaryGeneratedColumn({
        type:"bigint", 
        name:"id"
        })
    id:string;
        

    @Column("bigint",{ 
        nullable:false,
        primary:true,
        name:"height"
        })
    height:string;
        

    @Column("datetime",{ 
        nullable:true,
        name:"timestamp"
        })
    timestamp:Date | null;
        

   
    @ManyToOne(type=>users, users=>users.worker_sharess,{ onDelete: 'RESTRICT',onUpdate: 'RESTRICT' })
    @JoinColumn({ name:'user_id'})
    user_:users | null;


   
    @OneToMany(type=>shares, shares=>shares.parent_,{ onDelete: 'RESTRICT' ,onUpdate: 'RESTRICT' })
    sharess:shares[];
    
}
