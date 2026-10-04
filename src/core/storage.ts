import { emptyState,type Content,type UserState,type Backup } from './types.js';
import { validateBackup,validateContent } from './validation.js';
// Keep the existing production database; the preview gets its own learning history.
const DB_NAME=new URL('../',import.meta.url).pathname.endsWith('/develop/')?'step800-develop':'step800';
export function openDatabase():Promise<IDBDatabase> {
  return new Promise((resolve,reject)=>{
    const request=indexedDB.open(DB_NAME,1);
    request.onupgradeneeded=()=>{for(const name of ['state','content'])if(!request.result.objectStoreNames.contains(name))request.result.createObjectStore(name);};
    request.onsuccess=()=>resolve(request.result);request.onerror=()=>reject(request.error);request.onblocked=()=>reject(Error('別タブを閉じてから再読み込みしてください。'));
  });
}
export class Store {
  state:UserState=emptyState();
  private queue:Promise<unknown>=Promise.resolve();
  constructor(private db:IDBDatabase){}
  read<T>(table:string,key:string):Promise<T|undefined>{return new Promise((resolve,reject)=>{const request=this.db.transaction(table).objectStore(table).get(key);request.onsuccess=()=>resolve(request.result);request.onerror=()=>reject(request.error);});}
  async load(){this.state=await this.read<UserState>('state','user')??emptyState();return this.state;}
  async saveContent(content:Content){validateContent(content);await new Promise<void>((resolve,reject)=>{const tx=this.db.transaction('content','readwrite');tx.objectStore('content').put(content,'current');tx.oncomplete=()=>resolve();tx.onabort=()=>reject(tx.error);});}
  mutate(fn:(state:UserState)=>void):Promise<UserState>{
    const action=this.queue.then(()=>new Promise<UserState>((resolve,reject)=>{
      const tx=this.db.transaction('state','readwrite'),table=tx.objectStore('state');
      let next:UserState;let failure:unknown;
      const request=table.get('user');
      request.onsuccess=()=>{try{next=request.result??emptyState();fn(next);table.put(next,'user');}catch(error){failure=error;tx.abort();}};
      tx.oncomplete=()=>{this.state=next;resolve(next);};tx.onabort=()=>reject(failure??tx.error??Error('保存できませんでした。空き容量を確認してください。'));
    }));
    this.queue=action.catch(()=>undefined);return action;
  }
  async restore(input:unknown){const backup=validateBackup(input);await this.mutate(state=>Object.assign(state,structuredClone(backup.state)));}
  async backup(contentVersion:string):Promise<Backup>{await this.queue;return {app:'step800',schemaVersion:1,exportedAt:new Date().toISOString(),contentVersion,state:structuredClone(this.state)};}
}
