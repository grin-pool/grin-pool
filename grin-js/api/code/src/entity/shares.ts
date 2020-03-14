import {BaseEntity,Column,Entity,Index,JoinColumn,JoinTable,ManyToMany,ManyToOne,OneToMany,OneToOne,PrimaryColumn,PrimaryGeneratedColumn,RelationId} from "typeorm";
import {worker_shares} from "./worker_shares";


@Entity("shares",{schema:"pool"})
@Index("parent_id",["parent_",])
export class shares {

    @PrimaryGeneratedColumn({
        type:"bigint", 
        name:"id"
        })
    id:string;
        

    @Column("int",{ 
        nullable:true,
        name:"edge_bits"
        })
    edge_bits:number | null;
        

    @Column("bigint",{ 
        nullable:true,
        name:"difficulty"
        })
    difficulty:string | null;
        

    @Column("int",{ 
        nullable:true,
        name:"valid"
        })
    valid:number | null;
        

    @Column("int",{ 
        nullable:true,
        name:"invalid"
        })
    invalid:number | null;
        

    @Column("int",{ 
        nullable:true,
        name:"stale"
        })
    stale:number | null;
        

   
    @ManyToOne(type=>worker_shares, worker_shares=>worker_shares.sharess,{ onDelete: 'RESTRICT',onUpdate: 'RESTRICT' })
    @JoinColumn({ name:'parent_id'})
    parent_:worker_shares | null;

}
