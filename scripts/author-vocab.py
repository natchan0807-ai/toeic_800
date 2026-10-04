"""Convert independently authored vocabulary rows into versioned draft batches."""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POS = {'v':'verb','n':'noun','a':'adjective','r':'adverb','p':'preposition','c':'conjunction'}

def write_batch(number, rows, domain='office', difficulty='standard', extra=None):
    items=[]
    for line in rows.strip().splitlines():
        if not line.strip() or line.startswith('#'): continue
        fields = line.strip().split('|')
        assert len(fields) in (7,8,9), (number, len(fields), line)
        lemma,pos,meaning,example,translation,collocations,related=fields[:7]
        item_domain=fields[7] if len(fields)>7 else domain
        item_difficulty=fields[8] if len(fields)>8 else difficulty
        slug=lemma.replace(' ','-')
        item={'id':f'v-{slug}','version':VERSIONS.get(lemma,1),'lemma':lemma,'domain':item_domain,'difficulty':item_difficulty,
              'relatedWords':related.split(';'),'rationale':f'学習設計上の選定: {meaning}に関する日常・業務の表現を練習するため。公式頻度に基づく順位ではない。',
              'evidenceType':'design','sourceIds':['iibc-format','iibc-vocabulary-study'],'reviewStatus':'pending',
              'senses':[{'id':f'v-{slug}-1','pos':POS[pos],'meaningJa':meaning,'example':example,'translationJa':translation,'collocations':collocations.split(';')}]}
        if extra and lemma in extra:
            for sense in extra[lemma]:
                sp,sm,se,st,sc=sense
                item['senses'].append({'id':f'v-{slug}-{len(item["senses"])+1}','pos':POS[sp],'meaningJa':sm,'example':se,'translationJa':st,'collocations':sc.split(';')})
        items.append(item)
    assert len(items)==100, (number,len(items))
    assert len({i['lemma'] for i in items})==100
    target=ROOT/'content'/'batches'/f'vocab-{number:03}.json'
    target.write_text(json.dumps({'id':f'vocab-{number:03}','schemaVersion':1,'createdAt':datetime.now(timezone.utc).isoformat(),'author':'vocabulary_editor','model':None,'input':'research policy v1','status':'generated','items':items},ensure_ascii=False,indent=2)+'\n')
    print(f'{target.name}: {len(items)} entries, {sum(len(i["senses"]) for i in items)} senses')

BATCHES={}
EXTRA={}
VERSIONS={'start':2,'prepare':2}
BATCHES[1]=('office','foundation',r'''
approve|v|承認する|The manager approved our travel request.|部長は出張申請を承認しました。|approve a request|approval
apply|v|応募する、申請する|Lena applied for a sales position.|レナは営業職に応募しました。|apply for a position|application
arrange|v|手配する|I arranged a taxi for our guests.|来客のタクシーを手配しました。|arrange a taxi|arrangement
attend|v|出席する|All new staff attended the workshop.|新入社員全員が研修会に出席しました。|attend a workshop|attendance
avoid|v|避ける|Take the train to avoid traffic.|渋滞を避けるため電車を利用してください。|avoid traffic|avoidable|travel
book|v|予約する|We booked a room near the station.|駅の近くの部屋を予約しました。|book a room|booking|travel
borrow|v|借りる|May I borrow your calculator today?|今日は電卓を借りてもいいですか。|borrow a calculator|lender
cancel|v|取り消す|Heavy snow forced us to cancel the tour.|大雪でツアーを中止せざるを得ませんでした。|cancel a tour|cancellation|travel
check|v|確認する|Please check the address before sending this.|発送前に住所を確認してください。|check an address|verification
confirm|v|確認して確定する|The hotel confirmed our reservation by email.|ホテルは予約確定をメールで知らせました。|confirm a reservation|confirmation|travel
contact|v|連絡する|Contact the help desk for assistance.|支援が必要なら窓口に連絡してください。|contact the help desk|contact information
 deliver|v|配達する|The store delivers groceries every morning.|その店は毎朝食料品を配達します。|deliver groceries|delivery|logistics
 discuss|v|話し合う|We discussed the proposal over lunch.|昼食を取りながら提案について話しました。|discuss a proposal|discussion
 earn|v|稼ぐ|She earns extra income by tutoring.|彼女は個別指導で副収入を得ています。|earn income|earnings|finance
 expect|v|予想する、見込む|We expect the repairs to finish Friday.|修理は金曜日に終わる見込みです。|expect a delay|expectation
 explain|v|説明する|The guide explained the safety rules.|ガイドが安全規則を説明しました。|explain the rules|explanation
 fill|v|満たす|Fill the tank before returning the car.|車を返す前に燃料を満タンにしてください。|fill a tank|full|travel
 follow|v|従う|Please follow the instructions on the label.|ラベルの指示に従ってください。|follow instructions|following
 improve|v|改善する|Better lighting improved conditions in the office.|照明の改善で職場環境がよくなりました。|improve conditions|improvement
 include|v|含む|The price includes breakfast and parking.|料金には朝食と駐車が含まれます。|include breakfast|inclusion|travel
 introduce|v|紹介する|Let me introduce our new accountant.|新しい経理担当者を紹介します。|introduce a colleague|introduction
 invite|v|招待する|We invited our neighbors to dinner.|近所の人を夕食に招待しました。|invite guests|invitation|daily
 join|v|参加する|Would you like to join our team?|私たちのチームに参加しませんか。|join a team|membership|people
 keep|v|保管する|Keep your receipt until the refund arrives.|返金されるまで領収書を保管してください。|keep a receipt|retain|daily
 leave|v|去る、出発する|The last bus leaves at ten.|最終バスは10時に出発します。|leave the station|departure|travel
 lend|v|貸す|The library lends laptops to members.|図書館は会員にノートパソコンを貸します。|lend a laptop|loan|daily
 make|v|作る|This factory makes parts for bicycles.|この工場は自転車の部品を作ります。|make parts|manufacturer|business
 meet|v|会う|I met the designer at the entrance.|入口でデザイナーに会いました。|meet a client|meeting
 move|v|移動する|Our office moved to a larger building.|事務所は広い建物に移転しました。|move to a building|relocation
 offer|v|提供する|The clinic offers free health checks.|その診療所は無料の健康診断を提供します。|offer a service|offering|health
 order|v|注文する|We ordered new chairs for the lobby.|ロビー用の新しい椅子を注文しました。|order furniture|order form
 pay|v|支払う|You can pay by credit card.|クレジットカードで支払えます。|pay by card|payment|finance
 plan|v|計画する|They plan to open another branch.|彼らは別の支店を開く予定です。|plan an event|planning|business
 prepare|v|準備する|Please prepare the slides before tomorrow.|明日になる前にスライドを準備してください。|prepare slides|preparation
 promise|v|約束する|The supplier promised to deliver by noon.|供給業者は正午までの納品を約束しました。|promise to deliver|commitment|business
 provide|v|提供する|The venue provides tables and chairs.|会場では机と椅子を用意しています。|provide equipment|provider
 purchase|v|購入する|We purchased the equipment last month.|先月その機器を購入しました。|purchase equipment|buyer|business
 receive|v|受け取る|Did you receive the updated schedule?|更新された予定表を受け取りましたか。|receive a schedule|recipient
 recommend|v|勧める|The clerk recommended a lighter suitcase.|店員はもっと軽いスーツケースを勧めました。|recommend a product|recommendation|daily
 reduce|v|減らす|The new system reduced waiting times.|新しいシステムで待ち時間が減りました。|reduce waiting times|reduction|business
 remember|v|覚えている|I remember the name of that cafe.|そのカフェの名前を覚えています。|remember a name|memory|daily
 remind|v|思い出させる|Please remind me to call the dentist.|歯科医への電話を忘れないよう声をかけてください。|remind someone to call|reminder|daily
 rent|v|賃借する|We rented bicycles for the afternoon.|午後の間、自転車を借りました。|rent a bicycle|rental|travel
 repair|v|修理する|A technician repaired the broken printer.|技術者が故障したプリンターを修理しました。|repair a printer|repair shop|technology
 replace|v|交換する|We replaced the damaged window yesterday.|昨日、破損した窓を交換しました。|replace a window|replacement
 reply|v|返事をする|Please reply to this email by Tuesday.|火曜日までにこのメールに返信してください。|reply to an email|response
 report|v|報告する|Report any damage to the supervisor.|破損があれば監督者に報告してください。|report damage|reporter
 request|v|依頼する|The customer requested a printed receipt.|客は紙の領収書を求めました。|request a receipt|request form|business
 reserve|v|予約して確保する|I reserved two seats near the stage.|舞台近くの席を2つ予約しました。|reserve a seat|reservation|daily
 return|v|戻る|Our director returns from Osaka tonight.|取締役は今夜大阪から戻ります。|return from a trip|arrival|travel
 review|v|検討する、見直す|The team reviewed the budget carefully.|チームは予算を慎重に見直しました。|review a budget|reviewer
 save|v|節約する|Buying a monthly pass saves money.|定期券を買うと節約になります。|save money|savings|finance
 schedule|v|予定を組む|We scheduled the inspection for Monday.|点検を月曜日に予定しました。|schedule an inspection|timetable
 select|v|選ぶ|Select your preferred language from the menu.|メニューから希望の言語を選んでください。|select an option|selection|technology
 send|v|送る|I sent the samples by express mail.|速達でサンプルを送りました。|send samples|sender|logistics
 share|v|共有する|Our two teams share one meeting room.|2つのチームは1つの会議室を共有しています。|share a room|shared workspace
 sign|v|署名する|Please sign at the bottom of the form.|用紙の一番下に署名してください。|sign a form|signature
 spend|v|費やす|We spent three hours checking the figures.|数値の確認に3時間を費やしました。|spend time|expenditure
 start|v|始まる、始める|The orientation starts after lunch.|昼食後に説明会が始まります。|start a session|beginning
 submit|v|提出する|Submit your application before the deadline.|締め切り前に申請書を提出してください。|submit an application|submission
 suggest|v|提案する|Mina suggested holding the meeting online.|ミナはオンラインでの会議を提案しました。|suggest a solution|suggestion
 support|v|支援する|Local businesses support the annual festival.|地元企業は毎年の祭りを支援しています。|support an event|supporter|business
 take|v|乗り物を利用する|Take the elevator to the fifth floor.|エレベーターで5階へお越しください。|take the elevator|transport|travel
 tell|v|伝える|Tell the receptionist your appointment time.|受付係に予約時刻を伝えてください。|tell someone the time|inform
 thank|v|感謝する|We thanked the volunteers for their help.|ボランティアに支援への感謝を伝えました。|thank someone for help|thanks|people
 train|v|訓練する|The company trains all new drivers.|会社は新人運転手全員を訓練します。|train employees|training|business
 travel|v|旅行する、移動する|She travels abroad twice a year.|彼女は年に2回海外へ行きます。|travel abroad|traveler|travel
 try|v|試す|Try restarting the computer first.|まずパソコンの再起動を試してください。|try restarting|attempt|technology
 update|v|更新する|Please update your address in the system.|システムの住所情報を更新してください。|update an address|latest information|technology
 use|v|使う|Use the side entrance after six.|6時以降は脇の入口を使ってください。|use an entrance|usage
 visit|v|訪れる|Our sales team visited the new store.|営業チームは新店舗を訪問しました。|visit a store|visitor|business
 wait|v|待つ|Please wait here until your name is called.|名前が呼ばれるまでここでお待ちください。|wait for a turn|waiting room|daily
 welcome|v|歓迎する|We welcome feedback from every customer.|すべてのお客様のご意見を歓迎します。|welcome feedback|greeting|business
 accept|v|受け入れる|The store accepts returns within thirty days.|その店は30日以内の返品を受け付けます。|accept returns|acceptance|business
 achieve|v|達成する|The team achieved its monthly sales target.|チームは月間売上目標を達成しました。|achieve a target|achievement|business
 add|v|加える|Add your name to the mailing list.|配信リストに名前を追加してください。|add a name|addition
 adjust|v|調整する|Adjust the chair to a comfortable height.|椅子を快適な高さに調整してください。|adjust the height|adjustment
 advise|v|助言する|The agent advised us to book early.|担当者は早めの予約を勧めました。|advise someone to book|advice|travel
 agree|v|同意する|We agreed to extend the deadline.|締め切りの延長に同意しました。|agree to a proposal|agreement
 allow|v|許可する|This ticket allows entry to both museums.|この券で両方の博物館に入れます。|allow entry|permission|travel
 announce|v|発表する|The director announced the opening date.|取締役が開業日を発表しました。|announce a date|announcement|business
 answer|v|答える|A specialist will answer your questions.|専門家が質問に答えます。|answer a question|response
 apologize|v|謝罪する|We apologize for the delayed shipment.|発送の遅れをおわびします。|apologize for a delay|apology|business
 appear|v|現れる|A warning message appeared on the screen.|画面に警告メッセージが現れました。|appear on a screen|appearance|technology
 assess|v|評価する|Engineers assessed the damage after the storm.|技師が嵐の後の被害を評価しました。|assess damage|assessment|business
 assign|v|割り当てる|The supervisor assigned each worker a task.|監督者は各作業員に仕事を割り当てました。|assign a task|assignment
 assist|v|手伝う|Two volunteers assisted with registration.|2人のボランティアが受付を手伝いました。|assist with registration|assistance|people
 assume|v|そうだと考える、仮定する|I assumed the fee included delivery.|料金には配送料が含まれると思っていました。|assume the fee includes delivery|assumption|business
 attach|v|添付する|Attach a copy of your receipt.|領収書のコピーを添付してください。|attach a receipt|attachment
 attract|v|引き付ける|The exhibition attracted visitors from overseas.|展示会は海外からの来場者を引き付けました。|attract visitors|attraction|business
 available|a|利用できる|Free parking is available behind the hotel.|ホテルの裏で無料駐車場が利用できます。|available parking|availability|travel
 balance|n|残高|Check your account balance before paying.|支払い前に口座残高を確認してください。|account balance|balanced|finance
 benefit|n|利点、恩恵|Flexible hours are a major benefit.|柔軟な勤務時間は大きな利点です。|a major benefit|beneficial|people
 budget|n|予算|The renovation stayed within our budget.|改装は予算内に収まりました。|within the budget|budgeting|finance
 charge|n|料金|There is no charge for delivery.|配送料はかかりません。|delivery charge|fee|finance
 claim|v|請求する|Employees may claim travel expenses online.|従業員はオンラインで出張費を請求できます。|claim expenses|claim form|finance
 company|n|会社|The company opened a branch in Kobe.|その会社は神戸に支店を開きました。|join a company|corporation|business
 complete|v|完了する|We completed the project ahead of schedule.|予定より早く計画を完了しました。|complete a project|completion
 concern|n|懸念|Safety remains our main concern.|安全性は引き続き最大の懸念です。|a major concern|concerned
 consider|v|検討する|We are considering a different supplier.|別の供給業者を検討しています。|consider an option|consideration|business
''')
EXTRA[1]={
'apply':[('v','適用される','The discount applies to online orders.','割引はオンライン注文に適用されます。','apply to orders')],
'book':[('n','本','This book explains basic accounting.','この本は会計の基礎を解説しています。','read a book')],
'check':[('n','点検','The equipment needs a safety check.','その機器には安全点検が必要です。','a safety check')],
'keep':[('v','ある状態を保つ','Keep the emergency exit clear.','非常口をふさがないでください。','keep an exit clear')],
'leave':[('n','休暇','She is on leave until Thursday.','彼女は木曜日まで休暇中です。','on leave')],
'meet':[('v','条件などを満たす','This model meets our safety standards.','この型は当社の安全基準を満たしています。','meet a standard')],
'order':[('n','順序','List the names in alphabetical order.','名前をアルファベット順に並べてください。','in alphabetical order')],
'return':[('v','返却する','Return the key to reception.','鍵を受付に返してください。','return a key')],
'save':[('v','保存する','Save your work before closing the program.','プログラムを閉じる前に作業内容を保存してください。','save a file')],
'sign':[('n','標識','Follow the signs to baggage claim.','手荷物受取所への標識に従ってください。','follow the signs')],
'take':[('v','時間などがかかる','The repair will take two hours.','修理には2時間かかります。','take two hours')],
'charge':[('v','充電する','Charge the tablet before your trip.','旅行前にタブレットを充電してください。','charge a battery')],
'claim':[('v','主張する','The manufacturer claims this coating lasts longer.','メーカーはこの塗料がより長持ちすると主張しています。','claim an advantage')],
'complete':[('a','全部そろった、完全な','A complete list is available online.','完全な一覧をオンラインで確認できます。','a complete list')],
'concern':[('v','関係する','This notice concerns all building users.','この通知は建物の全利用者に関係します。','concern all staff')]
}

if __name__=='__main__':
    import sys
    for source in sorted(Path(__file__).parent.glob('author-vocab.[0-9][0-9][0-9].py')):
        exec(source.read_text(), globals())
    requested=[int(n) for n in sys.argv[1:]] or sorted(BATCHES)
    for number in requested:
        domain,difficulty,rows=BATCHES[number]
        write_batch(number,rows,domain,difficulty,EXTRA.get(number))
