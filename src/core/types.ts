export type Difficulty = 'foundation' | 'standard' | 'stretch';
export type Confidence = 'sure' | 'unsure' | 'guess' | null;
export type Recall = 'remembered' | 'unsure' | 'forgot';
export interface Source { id:string;url:string;title:string;checkedAt:string;publishedYear:number|null;scope:string;terms:string;limitations:string;evidenceType?:string }
export interface Skill { id:string;name:string;description:string;parent:string }
export interface Sense { id:string;pos:string;meaningJa:string;example:string;translationJa:string;collocations:string[] }
export interface Vocabulary { id:string;version:number;lemma:string;domain:string;difficulty:Difficulty;relatedWords:string[];rationale:string;evidenceType:string;sourceIds:string[];reviewStatus:string;senses:Sense[] }
export interface Question { id:string;version:number;type:'part5';stem:string;options:{id:string;text:string}[];answerId:string;translationJa:string;explanationJa:string;optionExplanations:Record<string,string>;skillId:string;secondarySkillIds:string[];vocabularySenseIds:string[];difficulty:Difficulty;familyId:string;sourceIds:string[];reviewStatus:string }
export interface ContentReview { targetId:string;targetVersion:number;decision:string;independentAnswerId?:string;issues:string[];reason:string;reviewerType?:string;createdAt?:string }
export interface Content { schemaVersion:1;version:string;generatedAt:string;sources:Source[];skills:Skill[];vocabulary:Vocabulary[];questions:Question[];reviews:ContentReview[];invalidated:string[] }
export interface Settings { targetScore:number;currentScore:number;sessionMinutes:number;timezone:string;evidenceThreshold:number;reviewIntervals:number[];reviewRatio:number;weakRatio:number }
export interface Attempt { id:string;questionId:string;questionVersion:number;familyId:string;skillId:string;optionId:string;correct:boolean;activeMs:number;confidence:Confidence;firstAttempt:boolean;reason:string|null;createdAt:string;sessionId:string;excluded:boolean }
export interface ReviewState { id:string;kind:'question'|'vocabulary';targetId:string;targetVersion:number;dueAt:string;stage:number;lastResult:Recall;count:number }
export interface SavedSense { id:string;vocabularyId:string;vocabularyVersion:number;savedAt:string;note:string;encounteredQuestionIds:string[] }
export interface PlanItem { kind:'question'|'vocabulary';targetId:string;version:number;mode:'new'|'review'|'check';reason:string }
export interface StudySession { id:string;mode:'study'|'check'|'review';items:PlanItem[];cursor:number;status:'active'|'paused'|'complete';createdAt:string;updatedAt:string;activeMs:number;itemActiveMs:number }
export interface ContentFlag { id:string;targetId:string;targetVersion:number;message:string;status:'open'|'resolved';createdAt:string;excludeFromStats?:boolean }
export interface RecallEvent { id:string;targetId:string;sessionId:string;result:Recall;createdAt:string }
export interface UserState { schemaVersion:1;settings:Settings;attempts:Attempt[];reviews:Record<string,ReviewState>;saved:Record<string,SavedSense>;sessions:StudySession[];flags:ContentFlag[];recalls:RecallEvent[];snapshots:Record<string,Question|Vocabulary>;checkDone:boolean }
export interface Backup { app:'step800';schemaVersion:1;exportedAt:string;contentVersion:string;state:UserState }
export const defaults:Settings={targetScore:800,currentScore:520,sessionMinutes:10,timezone:'Asia/Tokyo',evidenceThreshold:10,reviewIntervals:[1,3,7,14,30],reviewRatio:.5,weakRatio:.3};
export function emptyState():UserState {return {schemaVersion:1,settings:{...defaults,reviewIntervals:[...defaults.reviewIntervals]},attempts:[],reviews:{},saved:{},sessions:[],flags:[],recalls:[],snapshots:{},checkDone:false};}
export const refKey=(id:string,version:number)=>`${id}@${version}`;
export const reviewKey=(kind:'question'|'vocabulary',id:string)=>`${kind}:${id}`;
