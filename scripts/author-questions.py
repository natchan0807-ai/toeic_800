"""Reproducible authoring source for original, uncalibrated Part 5 practice.

Each source row is independently written. Families describe shared learning rules,
not production templates. All exported records remain pending until external review.
"""
import json
import random
import re
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = {}

def family(key, skill, explanation, *notes):
    assert len(notes) == 3
    FAMILIES[key] = (skill, explanation, notes)

family('noun-position', 'pos', '形容詞や所有格で修飾される名詞の位置です。', '形容詞なのでこの名詞の位置には置けません。', '副詞なのでこの名詞の位置には置けません。', '動詞なのでこの名詞の位置には置けません。')
family('adjective-position', 'pos', '名詞の性質を表す修飾語として形容詞が必要です。', '名詞なのでここでは名詞の性質を表せません。', '副詞では直後の名詞を修飾できません。', '動詞なのでこの修飾語の位置には置けません。')
family('adverb-position', 'pos', '動作の行い方や程度を説明する副詞が必要です。', '形容詞ではここで動作を修飾できません。', '名詞なので動作を修飾できません。', '動詞なのでこの修飾語の位置には置けません。')
family('past-specific', 'verb', '過去の特定の時点で完了した動作なので過去形を使います。', '現在形はこの過去の時点を表せません。', '未来形はこの過去の時点を表せません。', '現在完了形は終了した過去の時点を直接示す表現と合いません。')
family('modal-passive', 'verb', '主語が動作を受けるため、助動詞の後に be＋過去分詞を置きます。', '原形だけでは能動態となり、主語との関係が合いません。', '過去分詞の前に受動態の be が必要です。', 'be＋現在分詞は能動の進行形となり、主語との関係が合いません。')
family('perfect-since', 'verb', 'since で示した過去から現在までの継続には現在完了形を使います。', '過去形だけでは現在までの継続を表せません。', '現在形だけでは since の起点から続く期間を表せません。', '未来形では過去から現在までの継続を表せません。')
family('each-singular', 'agreement', 'each に導かれた単数の主語には単数形の述語を合わせます。', '複数主語に対応する形なので単数の主語に合いません。', '原形だけではこの単数主語の現在の述語になりません。', 'ing 形だけでは述語になりません。')
family('number-plural', 'agreement', 'a number of＋複数名詞は「多数の〜」で、述語は複数扱いです。', '単数形なので a number of＋複数名詞に合いません。', '動詞の原形はこの位置の定形の述語になりません。', 'ing 形だけでは述語になりません。')
family('head-singular', 'agreement', '主語の中心となる単数名詞に述語を一致させます。途中の修飾語の名詞には合わせません。', '複数形なので主語の中心の単数名詞に合いません。', '原形だけではこの単数主語の現在の述語になりません。', 'ing 形だけでは述語になりません。')
family('possessive-determiner', 'pronoun', '後ろの名詞に「誰のものか」を付け加える所有格が必要です。', '主格なので名詞の前で所有を示せません。', '目的格なので名詞の前で所有を示せません。', '独立所有代名詞は名詞を伴わず使うため、この位置には合いません。')
family('reflexive-object', 'pronoun', '主語と目的語が同一人物を指すので再帰代名詞を使います。', '主格は動詞の目的語になりません。', '所有格はこの位置の目的語になりません。', '独立所有代名詞では主語と同じ人物自身を表せません。')
family('object-pronoun', 'pronoun', '動詞や前置詞の目的語の位置なので目的格が必要です。', '主格なので目的語の位置には合いません。', '所有格は後ろに名詞を伴うため、この位置には合いません。', '独立所有代名詞ではここで意図する人物を表せません。')
family('deadline-by', 'preposition', '締め切りまでに動作を完了することを表す by が適切です。', 'until は動作や状態の継続する終点を表すため、この一回の完了の期限には合いません。', 'during は期間中を表し、この期限の表現には合いません。', 'since は過去の起点を表すため、この期限には合いません。')
family('duration-for', 'preposition', '動作や状態が続く長さを表す期間には for を使います。', 'since は期間の長さではなく開始時点を導きます。', 'by は完了の期限を表すため、この継続期間には合いません。', 'at は時点を表すため、この継続期間には合いません。')
family('interest-in', 'preposition', 'interest in は「〜への関心」を表す組み合わせです。', 'on はここで interest の対象を導く前置詞として使えません。', 'at はここで interest の対象を導く前置詞として使えません。', 'for はここで interest の対象を導く前置詞として使えません。')
family('although-clause', 'conjunction', '前後に対照的な内容があり、主語と動詞を伴う譲歩の節には although を使います。', 'despite は前置詞なので、この形の主語＋動詞の節を直接導けません。', 'because は理由を表し、この文の対照関係に合いません。', 'unless は「〜でない限り」で、この文の譲歩の関係に合いません。')
family('unless-condition', 'conjunction', 'unless は「〜しない限り」を表し、例外となる条件を導きます。', 'although は譲歩なので、必要条件を示す文意に合いません。', 'because は理由なので、例外の条件を示す文意に合いません。', 'once は「いったん〜すると」で、この否定的な条件とは意味が変わります。')
family('purpose-so-that', 'conjunction', '後続の主語＋動詞の節が目的を表すため so that を使います。', 'so as to の後には動詞の原形が必要で、主語＋動詞の節は続きません。', 'because of は前置詞句なので主語＋動詞の節を直接続けられません。', 'even though は譲歩で、この文の目的の関係に合いません。')
family('relative-person-subject', 'relative', '人を先行詞とし、関係節内で主語になる関係代名詞 who が適切です。', 'whom は目的格なので関係節の主語にはなれません。', 'whose は所有格で、直後に修飾する名詞が必要です。', 'which はこの人を指す先行詞には使えません。')
family('relative-thing-subject', 'relative', '物や事柄を先行詞とし、関係節の主語になる which が適切です。', 'who は人を表すため、この先行詞には合いません。', 'where は場所の副詞で、関係節の主語にはなれません。', 'whose は所有格で、ここで主語を単独で担えません。')
family('relative-possessive', 'relative', '先行詞との所有関係を表し、後ろの名詞を修飾する whose が必要です。', 'who は主格なので後ろの名詞の所有関係を示せません。', 'whom は目的格なので後ろの名詞の所有関係を示せません。', 'which はここで後ろの名詞の所有関係を示せません。')
family('comparative-than', 'comparison', 'than で二者を比較しているので比較級が必要です。', '原級はこの than の比較構文に合いません。', '最上級は二者を than で比較するこの構文に合いません。', '副詞ではこの位置で必要な形容詞の比較級を表せません。')
family('superlative-range', 'comparison', '明示された範囲の中で最も程度が高いものを表すので最上級を使います。', '原級では範囲内で最も程度が高いことを表せません。', '比較級はこの the と範囲の組み合わせによる最上級表現に合いません。', '副詞はここで名詞を修飾する形容詞の最上級にはなりません。')
family('as-positive', 'comparison', 'as＋形容詞の原級＋as で同じ程度を表します。', '比較級は as と as の間には置きません。', '最上級は as と as の間には置きません。', '副詞ではここで主語の性質を表す補語になれません。')
family('much-uncountable', 'determiner', '不可算名詞の量を表すため much を使います。', 'many は可算名詞の複数形を修飾します。', 'a few は可算名詞の複数形を修飾します。', 'several は可算名詞の複数形を修飾します。')
family('few-countable', 'determiner', '複数の可算名詞に対して少ない数を表す a few が適切です。', 'a little は不可算名詞の量を修飾します。', 'much は不可算名詞の量を修飾します。', 'each の直後には可算名詞の単数形を置きます。')
family('another-singular', 'determiner', '別の、または追加の一つの可算名詞には another を使います。', 'other はこの単数名詞を単独では修飾できません。', 'others は代名詞なので後ろに名詞を続けません。', 'every は「すべての」で、この追加の一つを求める文脈に合いません。')
family('lexical-context', 'vocabulary', '文全体の意味と、目的語や周囲の語との自然な組み合わせから選びます。', 'この文脈の意味に合いません。', 'この文脈の意味に合いません。', 'この文脈の意味に合いません。')

for lexical_family in ('authorization','rescheduling','replacement','finance','recruitment','delivery','communication','maintenance','compliance','inventory','reservation','evaluation','negotiation','quantity','location'):
    FAMILIES['lexical-'+lexical_family] = FAMILIES['lexical-context']

family('linking-adjective','pos','連結動詞の後で主語の状態や性質を述べる補語なので形容詞を使います。','副詞はここで主語の性質を表す補語にはなれません。','名詞ではここで求める性質を表せません。','動詞ではこの補語の位置に置けません。')
family('participle-cause','pos','物事が人に与える印象を表すため、能動的な意味の ing 形の形容詞を使います。','ed 形はその感情を抱く側を表し、印象を与える物事には合いません。','名詞はここで性質を表す形容詞の働きをしません。','動詞の原形はここで形容詞の働きをしません。')
family('participle-feeling','pos','人がある感情を抱いた状態を表す ed 形の形容詞が必要です。','この形容詞は他者にその印象を与える意味で、本人の感じ方を表せません。','名詞ではここで必要な感情の状態を表せません。','動詞の原形はこの補語の位置に合いません。')
family('future-progressive','verb','未来の特定の時点で進行中の動作なので未来進行形を使います。','過去進行形は未来の時点に合いません。','現在完了形は未来の進行中の動作を表せません。','過去完了形は未来の時点に合いません。')
family('infinitive-complement','verb','この動詞の後には to＋動詞の原形を続けて行為を表します。','この動詞はこの用法では ing 形を直接目的語に取りません。','過去分詞ではこの動詞の補足となる行為を表せません。','名詞ではここで後続の目的語を取る動詞の働きができません。')
family('gerund-complement','verb','この動詞や表現の後で行為を目的語にするときは動名詞を使います。','この表現の直後には to 不定詞を目的語として置けません。','動詞の原形を直接目的語として置けません。','過去形や過去分詞をこの目的語の位置には置けません。')
family('past-perfect','verb','過去のある時点より前に完了した動作なので過去完了形を使います。','現在完了形はこの過去を基準にした前後関係に合いません。','未来形は過去の時点より前の完了を表せません。','ing 形だけでは完了を表す述語になりません。')
family('finite-passive','verb','主語が動作を受けるため、be 動詞＋過去分詞の受動態を使います。','能動態では主語と動作の関係が逆になります。','ing 形だけではこの文の述語になりません。','to 不定詞だけではこの文の述語になりません。')
family('causative-base','verb','make や let の使役構文では目的語の後に動詞の原形を使います。','この使役構文では to 不定詞を置きません。','この能動の使役構文では ing 形を置きません。','過去形をこの位置に置くことはできません。')
family('both-plural','agreement','both に導かれた二つのものを表す主語には複数形の述語を使います。','単数形なので二つのものを表す主語に合いません。','原形はここで必要な定形の述語にはなりません。','ing 形だけでは述語になりません。')
family('uncountable-singular','agreement','主語が不可算名詞なので単数形の述語を合わせます。','複数形はこの不可算名詞の主語に合いません。','原形はここで必要な単数の述語になりません。','ing 形だけでは述語になりません。')
family('gerund-subject','agreement','動名詞句が一つの行為として主語になるので単数扱いです。','複数形は一つの行為を表す動名詞句の主語に合いません。','原形はこの単数扱いの主語の述語として不適切です。','ing 形だけでは述語になりません。')
family('one-of-singular','agreement','one of＋複数名詞では主語の中心は one なので、述語を単数にします。','of の後ろの複数名詞ではなく one に一致させる必要があります。','原形はこの単数主語の現在の述語になりません。','ing 形だけでは述語になりません。')
family('there-plural','agreement','there 構文では後ろの実質的な主語に動詞を一致させ、ここでは複数形を使います。','後ろの主語は複数なので単数形は合いません。','原形だけではこの文の述語になりません。','ing 形だけではこの文の述語になりません。')
family('neither-singular','agreement','neither of は「どちらも〜ない」で、ここでは単数形の述語を使います。','to 不定詞だけでは文の述語になりません。','動詞の原形だけではこの主語の現在の述語になりません。','ing 形だけでは述語になりません。')
family('independent-possessive','pronoun','名詞を繰り返さずに「〜のもの」を表す独立所有代名詞を使います。','所有格は名詞を伴って使うので、この単独の位置には合いません。','主格では所有物を表せません。','目的格では所有物を表せません。')
family('reflexive-emphasis','pronoun','主語の人物自身が行ったことを強調する再帰代名詞を使います。','所有格では人物自身という強調を表せません。','独立所有代名詞は所有物を表すのでここには合いません。','主格をこの位置に追加することはできません。')
family('one-substitute','pronoun','前に出た可算名詞を繰り返さず、別の一つを表す one を使います。','複数の ones はこの単数形を要求する修飾語に合いません。','it は同じ特定物を指し、この位置で別のものを修飾付きで表せません。','them は複数の目的格で、この位置で一つのものを表せません。')
family('those-substitute','pronoun','比較される複数名詞の繰り返しを避けるため those を使います。','単数を表す that では複数名詞を受けられません。','it は単数なので比較対象の複数名詞を受けられません。','its は所有格なので比較されるものを単独で表せません。')
family('on-date','preposition','曜日や特定の日付の前には on を使います。','in はこの特定の日付の前には使いません。','at は時刻などを示し、この日付の前には使いません。','of はこの日付で動作が行われることを示せません。')
family('between-two','preposition','二つの場所や対象の間という関係には between を使います。','among は集団の中の関係を表し、A and B という二項を結ぶこの形には合いません。','during は時間の期間を表し、二つの対象の関係には合いません。','within は範囲内を表し、A and B の二項間の関係には合いません。')
family('despite-noun','preposition','後ろが名詞句で、内容が譲歩を表すため despite を使います。','although は接続詞で、この名詞句だけを直接導けません。','because は接続詞で、理由を表す節が必要です。','unless は接続詞で、この名詞句だけを直接導けません。')
family('responsible-for','preposition','responsible for で「〜の責任がある・〜を担当する」を表します。','to は responsible の後では通常、責任を負う相手を示し、この担当業務を導く位置には合いません。','at はこの responsible の担当内容を導く組み合わせには使いません。','with はこの responsible の担当内容を導く組み合わせには使いません。')
family('according-to','preposition','according to は「〜によると」を表す固定した組み合わせです。','with は according とこの意味の組み合わせを作りません。','for は according とこの意味の組み合わせを作りません。','at は according とこの意味の組み合わせを作りません。')
family('in-month','preposition','月・年や比較的長い期間の中を示すには in を使います。','on は曜日や特定の日付に使い、この月や年だけの表現には合いません。','at は時刻などを示し、この月や年だけの表現には合いません。','of はここで実施される時期を示せません。')
family('because-clause','conjunction','後ろの主語＋動詞の節が理由を説明するので because を使います。','because of は前置詞句なので主語＋動詞の節を直接導けません。','despite は前置詞で、主語＋動詞の節を直接導けません。','unless は否定的な条件を表し、この理由の関係に合いません。')
family('before-clause','conjunction','手順上、一方を先に終えることを求めるため before で後の動作の節を導きます。','because of は名詞句を取り、この節を直接導けません。','during は前置詞なのでこの節を直接導けません。','despite は前置詞なのでこの節を直接導けません。')
family('while-clause','conjunction','二つの動作が同時に行われることを表す while が適切です。','during は前置詞なので主語＋動詞の節を直接導けません。','despite は前置詞なので主語＋動詞の節を直接導けません。','because of は前置詞句なので主語＋動詞の節を直接導けません。')
family('either-or','conjunction','either A or B で二つの選択肢を結びます。','and は either とこの選択の組み合わせを作りません。','nor は neither と対応する形で either には合いません。','but は either とこの選択の組み合わせを作りません。')
family('both-and','conjunction','both A and B で二つの要素をともに含むことを示します。','or は both とこの両方を示す組み合わせを作りません。','nor は both と対応しません。','but は both とこの両方を示す組み合わせを作りません。')
family('whether-or','conjunction','whether A or B で二つの可能性や選択肢を示します。','and はこの whether と組み合わせた二択を表せません。','nor は whether と対応しません。','but は whether とこの二択を表す組み合わせを作りません。')
family('relative-place','relative','関係節に主語と目的語があり、先行詞の場所でという関係を補う where を使います。','which を単独で置くと、関係節内に必要な場所の前置詞がなくなります。','who は人を表すため、この場所を指す先行詞に合いません。','whose は所有格で、この節を場所の関係で導けません。')
family('relative-time','relative','関係節の主語・目的語がそろっており、先行詞の時を示す関係副詞 when を使います。','which を単独で置くと、この関係節に必要な時の前置詞がなくなります。','who は人を指すため、時を表す先行詞には合いません。','whose は所有格で、時を表すこの節を導けません。')
family('relative-prep-person','relative','前置詞の後で人を先行詞とする関係代名詞は目的格 whom を使います。','who は主格なので、前置詞を直前に置くこの形には使いません。','that は直前に前置詞を置く関係節の形には使えません。','whose は所有格で、ここで前置詞の目的語にはなれません。')
family('relative-prep-thing','relative','前置詞の後で物を先行詞とする関係代名詞には which を使います。','that の直前に前置詞を置くことはできません。','who は人を表し、この物を表す先行詞に合いません。','where を前置詞の目的語として置くことはできません。')
family('fused-what','relative','先行詞を含んで「〜すること・もの」を表す what を使います。','which はここでは前に先行詞が必要です。','who は人物を表し、この内容や事柄を表す位置には合いません。','whose は所有格で、この位置で事柄を単独で表せません。')
family('comparative-modifier','comparison','比較級の程度を強める副詞には much を使えます。','very はこの比較級を直接強める形では使いません。','most はこの比較級を強めるために重ねて置けません。','many は可算名詞を修飾する語で、この比較級を強めません。')
family('fewer-countable','comparison','複数の可算名詞の数が少ないことを比較するので fewer を使います。','less は基本的に不可算名詞の量の比較に使い、この複数名詞の個数には合いません。','little は原級であり、この複数名詞と than の比較構文に合いません。','least は最上級であり、この than の比較構文に合いません。')
family('correlative-comparison','comparison','the＋比較級, the＋比較級 で「〜すればするほど…」を表します。','原級ではこの the を二度使う相関比較を作れません。','最上級ではこの相関比較を作れません。','副詞の原級ではこの位置の比較級になりません。')
family('double-as','comparison','倍数＋as＋原級＋as で「〜の何倍も…」を表します。','than は比較級に対応する語で、この原級の倍数表現には合いません。','that はこの同等比較の組み合わせを作りません。','so はこの肯定の倍数表現の後半には使えません。')
family('better-of-two','comparison','二つのもののうち優れた方を示すため、the と比較級を使います。','最上級はこの二者の比較では使いません。','原級では優れた方という比較を表せません。','副詞ではこの名詞を修飾する形容詞の比較級になりません。')
family('each-singular-noun','determiner','each の直後には単数の可算名詞を置き、個々を表します。','many は複数名詞を必要とするため、この単数名詞に合いません。','several は複数名詞を必要とするため、この単数名詞に合いません。','all はこの単数の可算名詞を単独では修飾できません。')
family('little-uncountable','determiner','不可算名詞の少量を表すので a little を使います。','a few は複数の可算名詞の数を表します。','many は複数の可算名詞を修飾します。','each は単数の可算名詞を修飾します。')
family('other-plural','determiner','other＋複数名詞で「ほかの〜」を表します。','another は単数名詞を伴うため、この複数名詞には合いません。','others は代名詞なので直後に名詞を続けません。','every の直後には単数名詞を置きます。')
family('article-an','determiner','直後の発音が母音で始まる単数の可算名詞なので、不定冠詞 an を使います。','a は直後の発音が子音で始まる場合に使うため、ここには合いません。','many は複数の可算名詞を要求します。','these は複数を示すため、この単数名詞に合いません。')
family('all-of-plural','determiner','all of＋限定された複数名詞で、そのすべてを表します。','every はこの形で of と直接つなげられません。','another は単数を表すため、この全体を示す構文には合いません。','much は不可算名詞の量を表し、この可算複数名詞には合いません。')
family('neither-two','determiner','二つのうちどちらも該当しないことを表す neither が適切です。','none はこの単数名詞の直前で限定詞として使えません。','every は三つ以上を念頭にすべてを表し、この二つを否定する文脈に合いません。','both は複数を伴うため、この単数名詞には合いません。')
family('preposition-gerund','verb','前置詞の後に動作を表す語を置くので動名詞を使います。','前置詞の後にはこの動詞の原形を直接置けません。','前置詞の後に to 不定詞は置けません。','過去形や過去分詞ではこの前置詞の目的語になりません。')
family('conditional-present','verb','未来のことでも条件を表す if 節内では現在形を使います。','通常の未来の条件節では will を用いた未来形にしません。','この具体的な未来の条件は現在形で示し、過去形は使いません。','ing 形だけでは if 節の述語になりません。')
family('subject-pronoun','pronoun','文の主語の位置なので主格の代名詞が必要です。','目的格はここで文の主語にはなれません。','所有格は名詞なしでこの主語の位置には使えません。','独立所有代名詞は所有物を表し、文脈上の人物を指せません。')
family('at-time','preposition','具体的な時刻の前には at を使います。','in はこの具体的な時刻の前には使いません。','on は曜日や日付の前に使い、時刻には合いません。','of はここで動作の時刻を示せません。')
family('depend-on','preposition','depend on で「〜に依存する・〜次第である」を表します。','at はこの depend の対象を導く組み合わせには使いません。','for はこの depend の条件を直接導く組み合わせには使いません。','to はこの depend の対象を導く組み合わせには使いません。')
family('within-period','preposition','ある長さの期間内に完了することを示す within を使います。','during は期間中を表しますが、この数値だけの期間の長さを直接続ける表現には合いません。','since は期間の長さではなく開始時点を導きます。','at は時点を表すため、この期間の長さを直接導けません。')
family('not-only-but','conjunction','not only A but also B で「AだけでなくBも」を表します。','and はこの not only と対応する形では使いません。','or はこの両方を述べる not only の組み合わせに合いません。','nor は not only とこの形で対応しません。')
family('less-uncountable','comparison','不可算名詞の量が少ないことを比較するので less を使います。','fewer は複数の可算名詞の数を比較します。','fewest は可算名詞の数の最上級で、この量の比較に合いません。','least は最上級で、この than を用いた比較に合いません。')
family('both-determiner','determiner','二つのものの両方を表す both は複数名詞を伴います。','either の直後には単数の可算名詞が必要です。','each の直後には単数の可算名詞が必要です。','another はこの複数名詞に直接続けられません。')

DATA = r'''
noun-position|The board gave its final _____ for the renovation, so work can begin next week.|approval/approving~approving は動名詞にもなりますが、承認を与える give one’s approval というこの名詞表現には合いません。/approvingly/approve|理事会が改修を最終承認したため、工事は来週始められます。
adjective-position|Applicants need to provide a _____ description of their previous responsibilities.|comprehensive/comprehension/comprehensively/comprehend|応募者は以前の職責を網羅的に説明したものを提出する必要があります。
adverb-position|Please read the cancellation policy _____ before you reserve a room.|carefully/careful/care/carefulness~carefulness は名詞で動作を修飾できません。|部屋を予約する前にキャンセル規定を注意深く読んでください。
past-specific|The facilities team _____ the damaged lock yesterday afternoon.|replaced/replaces/will replace/has replaced|施設管理チームは昨日の午後、破損した錠を交換しました。
modal-passive|All travel requests must _____ by a department manager before tickets are purchased.|be approved/approve/approved/be approving|航空券を購入する前に、すべての出張申請が部長の承認を受ける必要があります。
perfect-since|Ms. Chen _____ at the Osaka office since it opened in 2019.|has worked/worked/works/will work|チェンさんは2019年の開設以来、大阪事務所で働いています。
each-singular|Each participant _____ a printed schedule at the start of the workshop.|receives/receive~receive は複数主語に対応する現在形で each participant に合いません。/receiving~receiving だけでは述語になりません。/to receive~不定詞だけではこの文の述語になりません。|各参加者は研修の開始時に印刷された日程表を受け取ります。
number-plural|A number of local shops _____ now offering discounts to festival visitors.|are/is/be/being|多くの地元の店が現在、祭りの来場者に割引を提供しています。
head-singular|The list of available meeting rooms _____ on the reception desk.|is/are/be/being|利用可能な会議室の一覧は受付の机の上にあります。
possessive-determiner|We ask all visitors to keep _____ identification badges visible while in the building.|their/they/them/theirs|来訪者の皆様には、館内では身分証を見えるように着けていただくようお願いしています。
reflexive-object|Before meeting the clients, Mr. Park introduced _____ to the new project team.|himself/ourselves~ourselves は一人称複数を表し、三人称単数の Mr. Park に一致しません。/herself~女性を表す herself は Mr. Park に一致しません。/itself~物事を表す itself は人物の Mr. Park に使えません。|顧客に会う前に、パクさんは新しいプロジェクトチームに自己紹介しました。
object-pronoun|If you need a signed copy of the agreement, please contact _____ directly.|us/we/our/ours|契約書の署名済みの写しが必要な場合は、私たちに直接ご連絡ください。
deadline-by|To be included in this month's newsletter, submit your article _____ Friday at noon.|by/until/during/since|今月のニュースレターに掲載するには、金曜日の正午までに記事を提出してください。
duration-for|The replacement parts will be stored here _____ three weeks while the workshop is renovated.|for/since/by/at|作業場の改修中、交換部品はここで3週間保管されます。
interest-in|The survey revealed strong interest _____ a shuttle service between the station and the hotel.|in/on/at/for|調査により、駅とホテルを結ぶ送迎サービスへの強い関心が明らかになりました。
although-clause|_____ the auditorium was nearly full, the organizers found seats for our entire group.|Although/Despite/Because/Unless|講堂はほぼ満員でしたが、主催者は私たちのグループ全員の席を見つけてくれました。
unless-condition|Your reservation will be canceled _____ we receive payment by the end of today.|unless/although/because/once|本日中にお支払いをいただかない限り、ご予約は取り消されます。
purpose-so-that|The trainer spoke slowly _____ everyone could follow the safety instructions.|so that/so as to/because of/despite~despite は前置詞なので主語＋動詞の節を直接導けません。|全員が安全上の指示に従えるよう、講師はゆっくり話しました。
relative-person-subject|Employees _____ wish to join the weekend tour should sign up by Wednesday.|who/whom/whose/which|週末のツアーへの参加を希望する従業員は、水曜日までに申し込んでください。
relative-thing-subject|The new scanner, _____ can process both sides of a page, is beside the copier.|which/who/where/whose|用紙の両面を読み取れる新しいスキャナーは、コピー機の横にあります。
relative-possessive|We invited a consultant _____ experience includes several hospital construction projects.|whose/who/whom/which|私たちは複数の病院建設事業の経験を持つコンサルタントを招きました。
comparative-than|The express bus is _____ than a taxi for travelers on a tight budget.|cheaper/cheap/cheapest/cheaply|予算が限られた旅行者にとって、高速バスはタクシーより安価です。
superlative-range|Of the three proposals, the committee selected the _____ solution.|simplest/simplicity~simplicity は名詞で、ここで solution を修飾する形容詞になりません。/simpler/simply|委員会は3つの提案の中から最も簡単な解決策を選びました。
as-positive|After the repair, the original printer is as _____ as the newer model.|reliable/more reliable/most reliable/reliably|修理後、元のプリンターは新しい機種と同じくらい信頼性があります。
much-uncountable|There is not _____ space left in the cabinet, so please store the folders elsewhere.|much/many/a few/several|戸棚にはあまり空きがないので、書類ばさみは別の場所に保管してください。
few-countable|The designer made _____ minor changes before sending the final drawing to the client.|a few/a little/much/each|設計者は最終図面を顧客に送る前に、いくつか小さな変更を加えました。
another-singular|This projector is already booked, so we will need _____ one for the afternoon session.|another/other/others/every|このプロジェクターは予約済みなので、午後の回には別の1台が必要です。
lexical-authorization|The director cannot _____ the purchase until she has reviewed the cost estimate.|approve~approve は「承認する」で、見積り確認後に購入を認める文脈に合います。/borrow~borrow は「借りる」で、購入を認める意味になりません。/attend~attend は「出席する」で、購入を認める意味になりません。/repair~repair は「修理する」で、購入行為を目的語に取る文脈に合いません。|部長は費用の見積りを確認するまで購入を承認できません。|見積りを確認してから購入を認めるため approve が適切です。
lexical-rescheduling|Because the speaker's flight was canceled, the organizers had to _____ the seminar until Friday.|postpone~postpone は「延期する」で、金曜日まで日程を延ばす意味です。/publish~publish は「出版・公表する」でセミナーの日程変更に合いません。/collect~collect は「集める」で日程変更を表せません。/replace~replace は「取り替える」で until Friday が示す開催日の延期を表せません。|講演者の便が欠航したため、主催者はセミナーを金曜日まで延期しなければなりませんでした。|欠航により開催を後の日へ移すので postpone が適切です。
lexical-replacement|Please _____ the damaged cable with a new one before using the monitor.|replace~replace A with B は「AをBと取り替える」です。/remind~remind は「思い出させる」でケーブルの交換を表せません。/attend~attend は「出席する」でケーブルの交換を表せません。/borrow~borrow は「借りる」で replace A with B の交換の意味にはなりません。|モニターを使う前に、破損したケーブルを新しいものと交換してください。|破損した物を新しい物に交換する replace A with B が自然です。
'''

DATA += r'''
linking-adjective|Your membership card will remain _____ until the last day of December.|valid/validly/validity/validate|会員証は12月の最終日まで有効です。
participle-cause|The presenter used an _____ story to explain why customers value prompt service.|entertaining/entertained/entertainingly~副詞 entertainingly はここで名詞 story を直接修飾できません。/entertain|発表者は、顧客が迅速な対応を重視する理由を説明するために面白い話を使いました。
participle-feeling|The applicants were _____ to learn that the company had withdrawn the job offer.|disappointed/disappointing/disappointment/disappoint|応募者たちは、会社が採用の申し出を取り下げたと知って落胆しました。
future-progressive|At this time tomorrow, our engineers _____ the newly installed production line.|will be testing/were testing/have tested/had tested|明日の今頃、当社の技術者たちは新設の生産ラインを試験しているでしょう。
infinitive-complement|The gallery plans _____ its opening hours during the summer exhibition.|to extend/extending/extended/extension|美術館は夏の展覧会の期間中、開館時間を延長する予定です。
gerund-complement|The company is considering _____ a larger warehouse near the port.|leasing/to lease/lease/leased|会社は港の近くで、より大きな倉庫を賃借することを検討しています。
both-plural|Both copies of the signed contract _____ in the locked filing cabinet.|are/is/be/being|署名済みの契約書2部はどちらも、鍵のかかった書類棚に入っています。
uncountable-singular|The information on these labels _____ essential for identifying the correct replacement part.|is/are/be/being|これらのラベルに書かれた情報は、適切な交換部品を特定するために不可欠です。
gerund-subject|Checking the expiration dates on all products _____ part of the opening routine.|is/are/be/being|すべての商品の使用期限を確認することは、開店時の日課の一部です。
independent-possessive|The neighboring company has a large warehouse, but _____ is closer to the port.|ours/our/we/us|隣の会社には大きな倉庫がありますが、私たちの倉庫のほうが港に近いです。
reflexive-emphasis|The technicians installed the server _____, without assistance from the manufacturer.|themselves/their/theirs/they|技術者たちはメーカーの支援を受けずに、自分たちでサーバーを設置しました。
one-substitute|This suitcase is too heavy for the overhead shelf; do you have a lighter _____?|one/ones/it/them|このスーツケースは頭上の棚に置くには重すぎます。もっと軽いものはありますか。
on-date|The public library will reopen _____ Monday after a two-week renovation.|on/in/at/of|公共図書館は2週間の改修を終えて月曜日に再開します。
between-two|A covered walkway runs _____ the main terminal and the airport hotel.|between/among/during/within|屋根付きの通路が主要ターミナルと空港ホテルの間に伸びています。
despite-noun|_____ the heavy rain, the outdoor equipment remained dry under the new canopy.|Despite/Although/Because/Unless|激しい雨にもかかわらず、屋外の機器は新しいひさしの下でぬれずに済みました。
because-clause|The delivery was delayed _____ the access road was closed for emergency repairs.|because/because of/despite/unless|進入道路が緊急工事のため閉鎖されていたので、配送が遅れました。
before-clause|Please turn off the power _____ you remove the cover from the machine.|before/because of/during/despite|機械からカバーを外す前に電源を切ってください。
while-clause|Visitors can view the exhibition _____ they wait for the guided tour to begin.|while/during/despite/because of|来館者は、ガイド付きツアーの開始を待つ間に展示を見ることができます。
relative-place|The hotel has a quiet lounge _____ guests can read newspapers and enjoy coffee.|where/which/who/whose|そのホテルには、宿泊客が新聞を読んだりコーヒーを楽しんだりできる静かなラウンジがあります。
relative-time|Please indicate a time _____ our technician can visit your office.|when/which/who/whose|当社の技術者が御社の事務所を訪問できる時間をお知らせください。
relative-prep-person|The architect with _____ we discussed the extension has sent a revised drawing.|whom/who/that/whose|増築について私たちが相談した建築家から、修正図面が届きました。
comparative-modifier|With the new sorting system, packages reach the loading area _____ faster than before.|much/very/most/many|新しい仕分けシステムにより、荷物は以前よりずっと速く積み込み場所に届きます。
fewer-countable|The revised form requires _____ signatures than the old application form.|fewer/less/little/least|改訂版の用紙は、旧申請書よりも必要な署名の数が少なくなっています。
correlative-comparison|The earlier you reserve a seat, the _____ the range of departure times available.|wider/wide/widest/widely|早く席を予約すればするほど、選べる出発時刻の幅が広がります。
each-singular-noun|_____ employee must complete the online safety course before entering the laboratory.|Each/Many/Several/All|各従業員は、研究室に入る前にオンラインの安全講習を修了する必要があります。
little-uncountable|The soup needs _____ salt before it can be served to the guests.|a little/a few/many/each|お客様に出す前に、スープには少量の塩を加える必要があります。
other-plural|If the main entrance is crowded, visitors may use the _____ doors along the east wall.|other/another/others/every|正面入口が混雑している場合、来館者は東側の壁沿いにあるほかの扉を利用できます。
lexical-finance|Employees must attach receipts to their claims in order to receive _____ for travel expenses.|reimbursement~reimbursement は立て替え費用の払い戻しです。/recruitment~recruitment は人材の採用活動です。/maintenance~maintenance は保守管理です。/permission~permission は許可で、旅費の払い戻しを表しません。|従業員が旅費の払い戻しを受けるには、請求書に領収書を添付する必要があります。|旅費を立て替えた従業員への払い戻しなので reimbursement を使います。
lexical-recruitment|Because several experienced nurses have retired, the hospital plans to _____ additional staff.|recruit~recruit は新たな人員を採用することです。/refund~refund はお金を返すことです。/export~export は商品などを輸出することです。/manufacture~manufacture は製品を製造することです。|経験豊かな看護師が何人か退職したため、病院は追加の職員を採用する予定です。|退職で不足した職員を補うため、人を採用する recruit が合います。
lexical-delivery|Please enter the tracking number to check the current _____ of your shipment.|status~status は現在の状況を表します。/salary~salary は給与です。/vacancy~vacancy は欠員や空室です。/warranty~warranty は保証です。|荷物の現在の配送状況を確認するには、追跡番号を入力してください。|追跡番号で調べるのは荷物がどういう状況にあるかなので status を使います。
'''

DATA += r'''
noun-position|After reviewing the survey results, the manager offered several practical _____ for improving service.|suggestions/suggestive/suggestively/suggest|調査結果を確認した後、部長はサービス向上のための実用的な提案をいくつかしました。
adjective-position|The portable scanner is a _____ tool for employees who regularly work outside the office.|useful/use/usefully/utilize|携帯型スキャナーは、普段社外で働く従業員にとって便利な道具です。
adverb-position|The receptionist _____ explained how to reach the nearest subway station.|politely/polite/politeness/politenesses~politenesses は名詞の複数形で動作を修飾できません。|受付係は最寄りの地下鉄駅への行き方を丁寧に説明しました。
past-perfect|By the time the customer called, the warehouse _____ the missing item.|had located/has located/will locate/locating|顧客が電話した時には、倉庫はすでに不足していた品物を見つけていました。
finite-passive|The original painting _____ to the museum last year by a local collector.|was donated/donated/donating/to donate|その絵画の原画は昨年、地元の収集家によって博物館に寄贈されました。
causative-base|The new reporting system lets managers _____ daily sales figures from any office.|check/to check/checking/checked|新しい報告システムにより、管理職はどの事務所からでも日々の売上高を確認できます。
one-of-singular|One of the display screens _____ temporarily out of service.|is/are/be/being|展示用の画面の一つが、一時的に使用できなくなっています。
there-plural|There _____ several spare chairs in the storage room beside the auditorium.|are/is/be/being|講堂の隣の倉庫には予備の椅子が何脚かあります。
neither-singular|Neither of the proposed dates _____ convenient for our overseas partners.|is/to be/be/being|提案された二つの日程は、どちらも海外の取引先にとって都合がよくありません。
those-substitute|The rental rates in the city center are higher than _____ in the surrounding towns.|those/that/it/its|市中心部の賃料は、周辺の町の賃料より高いです。
possessive-determiner|Ms. Lee placed _____ laptop in a locker before joining the factory tour.|her/she/hers~hers は名詞を伴わずに所有物を表す形なので laptop の前には置けません。/herself~herself は再帰代名詞で、名詞の前の所有格になりません。|リーさんは工場見学に参加する前に、自分のノートパソコンをロッカーに入れました。
object-pronoun|The travel agent sent _____ a revised itinerary after we requested an earlier flight.|us/we/our/ours|私たちがもっと早い便を希望した後、旅行会社の担当者は修正版の旅程を私たちに送りました。
responsible-for|The evening supervisor is responsible _____ securing all entrances after the final tour.|for/to/at/with|夜間の監督者は、最後の見学の後ですべての入口を施錠する責任を負っています。
according-to|According _____ the revised schedule, the opening ceremony will begin at ten.|to/with/for/at|改訂された予定表によると、開会式は10時に始まります。
in-month|The company first introduced its paperless billing service _____ 2021.|in/on/at/of|会社が請求書の電子化サービスを初めて導入したのは2021年です。
either-or|Customers can either collect their purchases at the store _____ request home delivery.|or/and/nor/but|顧客は購入品を店で受け取るか、自宅配送を依頼できます。
both-and|The new job requires both technical knowledge _____ the ability to explain complex ideas clearly.|and/or/nor/but|その新しい仕事には、技術的知識と複雑な考えを明確に説明する能力の両方が必要です。
whether-or|Please let us know whether you will attend the morning session _____ not.|or/and/nor/but|午前の回に出席するかどうか、お知らせください。
relative-prep-thing|The account into _____ your refund was deposited is listed on the confirmation email.|which/that/who/where|返金が振り込まれた口座は、確認メールに記載されています。
fused-what|The production instructions contain _____ the customer requested for the product labels.|what/that~that では後続節内で欠けている目的語を補えません。/who/whose|製造指示書には、顧客が商品ラベルに求めた内容が記載されています。
relative-person-subject|The volunteers _____ helped set up the exhibition will receive free admission tickets.|who/whom/whose/which|展示の設営を手伝ったボランティアには、無料の入場券が配られます。
double-as|The new battery lasts twice as long _____ the battery supplied with the original model.|as/than/that/so|新しい電池は、旧型機に付属していた電池の2倍長持ちします。
better-of-two|After testing both cameras, the photographer chose the _____ of the two for indoor work.|better/best/good/well|両方のカメラを試した後、写真家は屋内での仕事用に二つのうち性能のよいほうを選びました。
comparative-than|With all furniture removed, the conference room looks _____ than it did yesterday.|larger/large/largest/largely|家具がすべて取り除かれ、会議室は昨日より広く見えます。
article-an|The museum is seeking _____ experienced curator to manage its new collection.|an/a/many/these|博物館は新しい収蔵品を管理するため、経験豊かな学芸員を探しています。
all-of-plural|_____ of the documents in this folder have been signed by the client.|All/Every/Another/Much|このフォルダーに入っている書類はすべて、顧客の署名済みです。
neither-two|The two access roads are both closed, so _____ road is available for today's delivery.|neither/none/every/both|二つの進入道路はともに閉鎖されているため、今日の配送にはどちらの道路も使えません。
lexical-communication|Please _____ all registered participants of the venue change by email.|notify~notify A of B はAにBを知らせる表現です。/donate~donate は寄付する意味で、参加者への通知を表せません。/operate~operate は操作・運営する意味で、参加者への通知を表せません。/inspect~inspect は点検する意味で、会場変更を知らせる文脈に合いません。|登録済みの参加者全員に、会場の変更をメールで知らせてください。|notify A of B の形で、参加者に変更を知らせます。
lexical-maintenance|Routine _____ of the elevators includes checking the cables and lubricating moving parts.|maintenance~maintenance は設備の保守管理です。/advertising~advertising は広告活動です。/recruitment~recruitment は人材の採用活動です。/reimbursement~reimbursement は費用の払い戻しです。|エレベーターの定期保守には、ケーブルの点検と可動部への注油が含まれます。|ケーブル点検や注油は設備を正常に保つ maintenance の作業です。
lexical-compliance|All food vendors must _____ with the health department's hygiene regulations.|comply~comply with は規則などに従う意味です。/compete~compete with は相手と競争する意味です。/consist~consist は通常 of などと使い、規則に従う意味になりません。/arrive~arrive は到着する意味で、規則に従うことを表せません。|すべての食品販売業者は、保健部門の衛生規則に従う必要があります。|規則の順守を示す comply with が文脈に合います。
'''

DATA += r'''
noun-position|The supplier has assured us that the replacement parts meet all safety _____.|requirements/required~required は分詞で、この名詞の位置には合いません。/repeatedly~repeatedly は副詞で名詞の位置には合いません。/require|供給業者は、交換部品がすべての安全要件を満たしていると保証しています。
linking-adjective|Please make sure your password is sufficiently _____ and does not contain your name or birth date.|secure/security~security は名詞で、この程度の副詞に修飾される性質の補語には合いません。/securely~securely は副詞で、password の性質を表す補語にはなりません。/securement~securement は名詞で、この位置の性質の補語には合いません。|パスワードが十分安全であり、氏名や生年月日を含んでいないことを確かめてください。
linking-adjective|The instructions seem _____, but a diagram would make them easier to follow.|clear/clearly/clarity/clarify|説明は明確に思えますが、図があればさらに理解しやすくなります。
perfect-since|The family _____ this bakery since 1985 and still makes bread using the original recipe.|has owned/owned/owns/will own|この家族は1985年以来このパン屋を所有し、現在も創業当時のレシピでパンを作っています。
past-specific|The research team _____ its preliminary findings at a conference last October.|presented/presents/will present/has presented|研究チームは昨年10月の学会で、予備的な調査結果を発表しました。
modal-passive|The emergency exits should _____ clear at all times, even during deliveries.|be kept/keep/kept/be keeping|搬入中でも、非常口は常にふさがないようにしておく必要があります。
each-singular|Each invoice _____ the order number and the customer's billing address.|includes/include~include はこの単数主語に対応する現在形ではありません。/including~including だけでは述語になりません。/to include~to 不定詞だけでは述語になりません。|各請求書には、注文番号と顧客の請求先住所が記載されています。
head-singular|The delivery of flowers to the conference rooms _____ scheduled for eight tomorrow morning.|is/are/be/being|会議室への花の配送は、明朝8時に予定されています。
number-plural|A number of passengers _____ waiting at the information counter for news about their flight.|are/is/be/being|多くの乗客が、便の情報を待って案内カウンターに並んでいます。
reflexive-object|The volunteers reminded _____ to lock the supply room before leaving the shelter.|themselves/ourselves~一人称複数の ourselves は三人称複数の主語に一致しません。/herself~単数女性の herself は複数の volunteers に一致しません。/itself~物を表す単数の itself は複数の人を指す volunteers に合いません。|ボランティアたちは避難所を出る前に備品室を施錠するよう、自分たちに言い聞かせました。
independent-possessive|I have already submitted my report, but Mr. Sato is still working on _____.|his~his はここで his report の繰り返しを避ける独立所有代名詞です。/he~he は主格なので前置詞 on の目的語になりません。/him~him は人物を指す目的格で、佐藤さんの報告書を表せません。/himself~himself は佐藤さん本人を表し、文脈上の報告書を表せません。|私はすでに報告書を提出しましたが、佐藤さんはまだ自分の報告書を作成しています。
one-substitute|Our old refrigerator uses too much electricity, so we are looking for a more efficient _____.|one/ones/it/them|古い冷蔵庫は電気を使いすぎるため、私たちはもっと効率のよいものを探しています。
interest-in|Several investors expressed interest _____ the company's new recycling technology.|in/on/at/for|複数の投資家が、その会社の新しいリサイクル技術に関心を示しました。
duration-for|Guests may borrow bicycles _____ up to four hours at no additional charge.|for/since/by/at|宿泊客は追加料金なしで、最長4時間自転車を借りられます。
deadline-by|Please complete your meal selection _____ 6 p.m. so the caterer can place the food order.|by/until/during/since|仕出し業者が食材を発注できるよう、午後6時までに食事の選択を完了してください。
unless-condition|We cannot issue a refund _____ you provide the original receipt or another proof of purchase.|unless/although/because/once|領収書の原本か別の購入証明をご提示いただかない限り、返金することはできません。
although-clause|_____ the replacement part was expensive, the repair was still cheaper than buying a new machine.|Although/Despite/Because/Unless|交換部品は高価でしたが、それでも修理のほうが新しい機械を買うより安く済みました。
purpose-so-that|The guide distributed maps _____ visitors could explore the historic district on their own.|so that/so as to/because of/despite~despite は前置詞で、この主語＋動詞の節を直接導けません。|来訪者が自分たちで歴史地区を散策できるよう、ガイドは地図を配りました。
relative-possessive|Customers _____ subscriptions expire this month will receive a renewal notice next week.|whose/who/whom/which|今月購読期限が切れるお客様には、来週更新のお知らせをお送りします。
relative-thing-subject|The bus route, _____ connects the airport with three hotels, operates every thirty minutes.|which/who/where/whose|空港と三つのホテルを結ぶそのバス路線は、30分おきに運行しています。
relative-place|The company rents a workshop _____ local artists can produce furniture from recycled wood.|where/which/who/whose|会社は、地元の芸術家が再生木材で家具を製作できる作業場を借りています。
as-positive|The smaller meeting room is as _____ as the main hall when the windows are open.|bright/brighter/brightest/brightly|窓を開けると、小さい会議室は大広間と同じくらい明るくなります。
superlative-range|Among all the printers tested, this model had the _____ operating cost.|lowest/lowness~lowness は名詞で cost の程度を表す形容詞ではありません。/lower/lowly~lowly は「身分が低い」などを表し、費用の最小値には合いません。|試験したすべてのプリンターの中で、この機種の運用費が最も低くなりました。
fewer-countable|The hotel received _____ complaints after extending the breakfast service until ten.|fewer/less~less は不可算名詞の量を比較する語で、複数の苦情の件数には合いません。/little~little は不可算名詞の少量を表し、複数の complaints に合いません。/least~least は量の最上級で、前後の苦情件数の比較には合いません。|ホテルは朝食の提供時間を10時まで延長した後、苦情の件数が減りました。|complaints は複数の可算名詞で、延長前より少ない件数を表す比較級 fewer が適切です。
much-uncountable|The technician did not need _____ time to identify the source of the noise.|much/many/a few/several|技術者は騒音の原因を特定するのに、あまり時間を必要としませんでした。
few-countable|Please bring _____ extra batteries in case the wireless microphone stops working.|a few/a little/much/each|ワイヤレスマイクが動かなくなった場合に備え、予備の電池を何本か持ってきてください。
another-singular|The first sample was damaged in transit, so the supplier agreed to send _____ sample.|another/other/others/every|最初のサンプルが輸送中に破損したため、供給業者はもう一つサンプルを送ることに同意しました。
lexical-inventory|The store conducts a monthly _____ to determine how many items remain on its shelves.|inventory~inventory は在庫の点検・棚卸しを表します。/interview~interview は面接や取材です。/seminar~seminar は研修会や講習会です。/refund~refund は返金です。|店では棚に残っている商品の数を確認するため、毎月棚卸しを行います。|商品の現物数を確認する作業なので inventory が適切です。
lexical-reservation|Before you make travel arrangements, please check room _____ for the dates of your visit.|availability~availability は利用可能であることや空き状況です。/accuracy~accuracy は正確さです。/loyalty~loyalty は忠実さです。/profitability~profitability は収益性です。|旅行の手配をする前に、訪問予定日の客室の空き状況を確認してください。|希望日に客室が利用できるかを調べるので availability を使います。
lexical-evaluation|The committee will _____ each proposal against the same set of selection criteria.|evaluate~evaluate は基準に照らして評価する意味です。/evacuate~evacuate は避難させる意味です。/decorate~decorate は装飾する意味です。/duplicate~duplicate は複製する意味です。|委員会は、各提案を同じ一連の選定基準に照らして評価します。|選定基準に照らして提案を評価する動作は evaluate です。
'''

DATA += r'''
participle-cause|The sudden cancellation of the order was _____ for the team that had spent weeks preparing it.|frustrating/frustrated/frustration/frustrate|何週間も準備してきたチームにとって、その注文の突然の取り消しはもどかしいものでした。
participle-feeling|The visitors were _____ by the guide's detailed knowledge of the building's history.|impressed/impressive/impression/impress|来訪者たちは、その建物の歴史に関するガイドの詳しい知識に感心しました。
adverb-position|The accounting team worked _____ to complete the audit before the deadline.|efficiently/efficient/efficiency/efficiencies~efficiencies は名詞の複数形で、動作を修飾できません。|経理チームは、期限までに監査を終えるため効率よく働きました。
infinitive-complement|The hotel has agreed _____ the guests for the extra transportation costs.|to reimburse/reimbursing/reimbursed/reimbursement|ホテルは、宿泊客の追加交通費を払い戻すことに同意しました。
gerund-complement|To reduce the risk of damage, avoid _____ heavy boxes on top of the monitors.|placing/to place/place/placed|破損の危険を減らすため、モニターの上に重い箱を置くことは避けてください。
past-perfect|By the time the guests reached the dining room, the staff _____ every table.|had prepared/has prepared/will prepare/preparing|客が食堂に着いた時には、スタッフはすべてのテーブルの準備を終えていました。
both-plural|Both the invoice and the delivery note _____ attached to this email.|are/is/be/being|請求書と納品書の両方を、このメールに添付しています。
uncountable-singular|The equipment used in our laboratories _____ inspected at the beginning of every month.|is/are/be/being|当社の研究室で使う機器は、毎月初めに点検されます。
gerund-subject|Providing clear directions to first-time visitors _____ especially important at this large venue.|is/are/be/being|この大きな会場では、初めての来場者にわかりやすい案内をすることが特に大切です。
possessive-determiner|The company will send _____ annual report to shareholders at the end of April.|its/it/itself~itself は再帰代名詞で、名詞の前で所有を表せません。/it's~it's は it is または it has の短縮形で、所有格ではありません。|会社は4月末に年次報告書を株主へ送付します。
reflexive-emphasis|I checked the figures _____ before forwarding the report to the director.|myself/my/mine/I|私は部長に報告書を転送する前に、自分で数値を確認しました。
those-substitute|The safety requirements for this site are stricter than _____ for our smaller workshop.|those/that/it/its|この現場の安全要件は、当社の小さな作業場の要件より厳しくなっています。
on-date|The final rehearsal will take place _____ July 16 in the main auditorium.|on/in/at/of|最終リハーサルは7月16日に大講堂で行われます。
in-month|Demand for portable heaters usually rises _____ winter.|in/on/at/of|携帯型暖房器具の需要は、通常冬に増加します。
between-two|Negotiations _____ the landlord and the tenant continued until an agreement was reached.|between/among/during/within|家主と借主の交渉は、合意に達するまで続きました。
because-clause|Please use the side entrance _____ the main doors are being repainted.|because/because of/despite/unless|正面の扉を塗り直しているため、脇の入口をご利用ください。
while-clause|The software displays a progress bar _____ the files are being transferred.|while/during/despite/because of|ファイルの転送中、ソフトウェアは進行状況を示すバーを表示します。
either-or|The missing receipt can be sent either by regular mail _____ as an email attachment.|or/and/nor/but|不足している領収書は、普通郵便かメールの添付ファイルで送れます。
relative-time|The calendar shows the dates _____ the training center can accommodate large groups.|when/which/who/whose|カレンダーには、研修施設が大人数のグループを受け入れられる日が示されています。
relative-prep-person|The supplier from _____ we ordered the fabric has offered to replace the damaged rolls.|whom/who/that/whose|生地を注文した供給業者は、破損したロール状の生地を交換すると申し出ました。
relative-thing-subject|The warranty, _____ covers manufacturing defects, is valid for two years.|which/who/where/whose|製造上の欠陥を対象とするその保証は、2年間有効です。
comparative-than|With direct access to the highway, the new warehouse is _____ than our previous facility.|more convenient/convenient/most convenient/conveniently|高速道路に直接つながる新しい倉庫は、以前の施設より便利です。
as-positive|The revised application process is as _____ as the one used at our other branches.|simple/simpler/simplest/simply|改訂された申請手続きは、当社のほかの支店で使われているものと同じくらい簡単です。
superlative-range|Of all the shipping options listed, overnight delivery is the _____.|most expensive/expense~expense は名詞で、この補語の位置に必要な程度の表現ではありません。/more expensive/expensively|記載されているすべての配送方法の中で、翌日配達が最も高額です。
each-singular-noun|Please write the delivery date on _____ package before moving it to the loading area.|each/many/several/all|積み込み場所へ移す前に、各荷物に配達日を書いてください。
little-uncountable|We have _____ time before the presentation, so let's test the microphone now.|a little/a few/many/each|発表まで少し時間があるので、今マイクを試しましょう。
article-an|The position offers _____ opportunity to work closely with experienced editors.|an/a/many/these|その職では、経験豊かな編集者と密接に協力して働く機会が得られます。
lexical-negotiation|The purchasing team negotiated a ten-percent _____ on the order because it was buying in bulk.|discount~discount は通常価格からの値引きです。/deposit~deposit は保証金や手付金で、まとめ買いの値引きを表せません。/deficit~deficit は赤字や不足です。/deadline~deadline は締め切りです。|購買チームは大量購入のため、その注文について10％の値引きを交渉しました。|まとめ買いを理由に価格を下げてもらう交渉なので discount が適切です。
lexical-quantity|The factory increased production to meet the unexpected _____ in demand for water filters.|surge~surge は急増を表します。/shortage~shortage は不足で、需要の増大を表せません。/refund~refund は払い戻しです。/delay~delay は遅れで、生産増の理由となる需要の急増とは異なります。|工場は、浄水器の予想外の需要急増に応えるため生産を増やしました。|需要が予想外に増えたため増産したという流れには surge が合います。
lexical-location|The restaurant is _____ to the theater, allowing guests to walk directly from dinner to the performance.|adjacent~adjacent to は「〜に隣接した」です。/opposed~opposed to は「〜に反対した」で位置を表しません。/immune~immune to は「〜への免疫がある」です。/equivalent~equivalent to は「〜に相当する」で隣接を表しません。|レストランは劇場に隣接しているため、客は夕食から公演へ直接歩いて移動できます。|二つの施設の近い位置関係を説明する adjacent to が自然です。
'''

DATA += r'''
adjective-position|The training manual contains _____ advice on dealing with dissatisfied customers.|practical/practice/practically/practicing~practicing は動作中の意味を持つ分詞で、advice の有用な性質を表しません。|研修用マニュアルには、不満を持つ顧客への対応に関する実用的な助言が載っています。
noun-position|The architect requested written _____ that the revised design met local building codes.|confirmation/confirmatory/confidently~confidently は副詞なので名詞の位置に置けません。/confirm|建築家は、修正した設計が地域の建築規則に適合しているという書面での確認を求めました。
adverb-position|The replacement software _____ reduces the time needed to prepare monthly invoices.|significantly/significant/significance/signify|代わりに導入するソフトウェアは、月々の請求書作成に必要な時間を大幅に短縮します。
future-progressive|At noon next Friday, the delegates _____ through the newly completed exhibition hall.|will be walking/were walking/have walked/had walked|来週金曜日の正午、代表者たちは完成したばかりの展示ホールを歩いているでしょう。
finite-passive|The access code _____ every Monday by the building's security administrator.|is changed/changes/changing/to change|入館コードは毎週月曜日、建物の防犯管理者によって変更されます。
causative-base|The supervisor made the crew _____ the damaged railing before reopening the platform.|replace/to replace/replacing/replaced|監督者は、ホームを再開する前に破損した手すりを作業員に交換させました。
one-of-singular|One of the benefits of this service _____ free technical support on weekends.|is/are/be/being|このサービスの利点の一つは、週末の無料の技術サポートです。
there-plural|There _____ two important conditions that applicants must meet to receive the scholarship.|are/is/be/being|奨学金を受け取るために応募者が満たすべき、二つの重要な条件があります。
head-singular|The box containing the spare keys _____ kept behind the reception counter.|is/are/be/being|予備の鍵が入った箱は、受付カウンターの後ろに保管されています。
object-pronoun|The committee has reviewed your proposal and will send _____ its decision next week.|you/your~your は所有格で、動詞 send の目的語にはなりません。/yours~yours は所有物を表し、通知を受け取る相手そのものを指せません。/yourself~主語 the committee と受取人が同一ではないので、ここで再帰代名詞は使いません。|委員会はあなたの提案を検討済みで、来週その決定をあなたに送ります。
independent-possessive|Our team uses shared desks, whereas the design team has a dedicated room of _____.|theirs/their/they/them|私たちのチームは机を共用していますが、設計チームには自分たち専用の部屋があります。
reflexive-emphasis|Ms. Ortiz handled the complaint _____ instead of passing it to another department.|herself/her/hers/she|オルティスさんは苦情をほかの部署に回さず、自分で対応しました。
responsible-for|The event coordinator is responsible _____ arranging transportation for visiting speakers.|for/to/at/with|催事の調整担当者は、来訪する講演者の交通手段を手配する責任を負っています。
despite-noun|The delivery team arrived on time _____ the unusually heavy traffic near the stadium.|despite/although/because/unless|競技場付近の異常な渋滞にもかかわらず、配送チームは時間どおりに到着しました。
according-to|According _____ the latest weather report, the ferry service may be suspended this evening.|to/with/for/at|最新の天気予報によると、フェリーは今晩運休する可能性があります。
both-and|The exhibition attracted both professional designers _____ students interested in sustainable materials.|and/or/nor/but|その展示会は、プロの設計者と持続可能な素材に関心を持つ学生の両方を引きつけました。
whether-or|The support desk will ask whether you have restarted your computer _____ not.|or/and/nor/but|サポート窓口では、コンピューターを再起動したかどうか尋ねます。
before-clause|Inspect the packaging for visible damage _____ you sign the delivery receipt.|before/because of/during/despite|受領書に署名する前に、梱包に目に見える損傷がないか確認してください。
relative-prep-thing|The platform on _____ the orchestra will perform must be reinforced by a technician before the concert.|which/that/who/where|オーケストラが演奏する舞台は、コンサートの前に技術者が補強する必要があります。
fused-what|The revised handbook explains _____ employees should do when they discover a safety hazard.|what/that~that では後続節内で欠けている目的語を補えません。/who/whose|改訂された手引きには、従業員が安全上の危険を発見したときにすべきことが説明されています。
relative-possessive|The award went to a small company _____ products are made entirely from recycled materials.|whose/who/whom/which|その賞は、すべて再生素材で製品を作る小さな会社に贈られました。
comparative-modifier|The revised map makes the walking route _____ easier to understand than the old version did.|much/very/most/many|改訂された地図は、旧版よりも徒歩の経路をずっとわかりやすくしています。
correlative-comparison|The more thoroughly you prepare the surface, the _____ the new paint will last.|longer/long/longest/length~length は名詞で、この相関比較の比較級になりません。|表面を入念に下処理すればするほど、新しい塗装が長持ちします。
double-as|The storage tank can now hold three times as much water _____ it held before the expansion.|as/than/that/so|その貯水槽は現在、拡張前の3倍の水を貯められます。
other-plural|This elevator is reserved for equipment; please use the _____ elevators to reach the upper floors.|other/another/others/every|このエレベーターは機器専用です。上の階へはほかのエレベーターをご利用ください。
all-of-plural|_____ of our international branches use the same system for tracking customer orders.|All/Every/Another/Much|当社の海外支店はすべて、顧客の注文の追跡に同じシステムを使っています。
neither-two|We compared two venues, but _____ venue had enough parking spaces for all the guests.|neither/none/every/both|二つの会場を比較しましたが、どちらの会場にも来賓全員分の駐車スペースはありませんでした。
lexical-authorization|The contractor must obtain the owner's written _____ before making structural changes to the property.|consent~consent は同意・承諾です。/expense~expense は費用です。/attendance~attendance は出席です。/competition~competition は競争です。|請負業者は、建物の構造を変更する前に所有者の書面による同意を得る必要があります。|所有者から変更の許しを得るので written consent が適切です。
lexical-rescheduling|To accommodate the visiting auditor, we need to _____ the meeting from Tuesday to Wednesday.|reschedule~reschedule は予定の日時を変更する意味です。/recycle~recycle は再生利用する意味です。/refund~refund は返金する意味です。/reveal~reveal は明らかにする意味で、日時の変更を表せません。|来訪する監査人に合わせ、会議を火曜日から水曜日へ変更する必要があります。|会議自体を取り消さずに開催日を移すので reschedule を使います。
lexical-replacement|Before ordering a replacement battery, make sure it is _____ with your laptop model.|compatible~compatible with は機器などと適合して使えることを表します。/eligible~eligible は資格や条件を満たす意味で、電池と機器の互換性を表せません。/familiar~familiar は慣れている・よく知る意味で、電池の互換性を表せません。/responsible~responsible は責任がある意味で、電池の互換性を表せません。|交換用電池を注文する前に、使用しているノートパソコンの機種と適合するか確認してください。|電池をその機種で使用できるかという適合性を表す compatible が正解です。
'''

DATA += r'''
linking-adjective|The theater will stay _____ while inspectors examine the damage to the ceiling.|closed/closely~closely は副詞で、営業状態を表すこの補語には合いません。/closure/close~close はここでは「近い」などの意味になり、休館中という状態を表せません。|検査員が天井の損傷を調べる間、劇場は休館を続けます。
participle-cause|Many users found the original registration form _____, so we simplified the instructions.|confusing/confused/confusion/confuse|多くの利用者が元の登録用紙をわかりにくいと感じたため、説明を簡潔にしました。
participle-feeling|We were _____ to hear that the new recycling program had attracted so many volunteers.|pleased/pleasing/pleasure/please|新しいリサイクル計画に多くのボランティアが集まったと聞き、私たちは喜びました。
preposition-gerund|We look forward to _____ your team at the international trade fair next month.|meeting/meet/to meet/met|来月の国際見本市で皆様のチームにお会いするのを楽しみにしています。
conditional-present|If the replacement motor _____ tomorrow, the technician will install it before the weekend.|arrives/will arrive/arrived/arriving|交換用のモーターが明日届けば、技術者は週末までに取り付けます。
gerund-complement|The marketing department has finished _____ the survey responses from last month's event.|analyzing/to analyze/analyze/analyzed|マーケティング部門は、先月の催事のアンケート回答の分析を終えました。
head-singular|The quality of the ingredients _____ the flavor of the finished dish.|affects/affect~affect は複数主語に対応する現在形で、単数の quality に一致しません。/to affect~to 不定詞だけではこの文の述語になりません。/affecting|材料の品質が、完成した料理の風味に影響します。
both-plural|Both instructors _____ practical examples to explain the new accounting rules.|use/uses~uses は単数主語に対応する形で、both instructors に合いません。/to use~to 不定詞だけでは文の述語になりません。/using|二人の講師はともに、実例を使って新しい会計規則を説明します。
each-singular|Each of the storage cabinets _____ a label showing its contents.|has/have~have は複数主語に対応し、主語の each に合いません。/to have~to 不定詞だけでは文の述語になりません。/having|保管棚にはそれぞれ、中身を示すラベルが付いています。
subject-pronoun|The new assistants have completed their training, and _____ will begin work on Monday.|they/them/their/theirs|新しいアシスタントたちは研修を終え、月曜日から勤務を始めます。
object-pronoun|When the guide called my name, I handed _____ my ticket and entered the exhibition.|her/she/hers~hers は所有物を表すため、切符を受け取る人物を指せません。/herself~主語 I と相手が同一ではないので再帰代名詞を使いません。|ガイドが私の名前を呼んだとき、私は彼女に切符を渡して展示会場に入りました。
reflexive-emphasis|We assembled the display stands _____ using the instructions supplied with the kit.|ourselves/our/ours/we|私たちはキットに付属の説明書を使い、自分たちで展示台を組み立てました。
at-time|The last shuttle bus leaves the convention center _____ 9:15 p.m.|at/in/on/of|最後の送迎バスは、午後9時15分に会議場を出発します。
depend-on|The final delivery date will depend _____ the availability of the imported components.|on/at/for/to|最終的な納期は、輸入部品を入手できるかどうかで決まります。
within-period|Customers must report any missing items _____ 48 hours of receiving their order.|within/during/since/at|お客様は、注文品を受け取ってから48時間以内に不足品を申告する必要があります。
not-only-but|The new facility includes not only a swimming pool _____ also a fully equipped fitness studio.|but/and/or/nor|新施設にはプールだけでなく、設備の整った運動スタジオもあります。
because-clause|The manager approved a second service counter _____ the waiting time had doubled.|because/because of/despite/unless|待ち時間が2倍になっていたため、部長は二つ目のサービス窓口の設置を承認しました。
unless-condition|The system will not save your changes _____ you click the confirmation button.|unless/although/because/once|確認ボタンをクリックしない限り、システムは変更を保存しません。
relative-person-subject|We are seeking a translator _____ can work with technical documents in both languages.|who/whom/whose/which|私たちは、両言語の技術文書を扱える翻訳者を探しています。
relative-place|Please indicate the room _____ you would like us to install the new air conditioner.|where/which/who/whose|新しいエアコンの設置をご希望の部屋をお知らせください。
relative-prep-thing|The survey identifies the services for _____ customers are willing to pay an additional fee.|which/that/who/where|調査は、顧客が追加料金を払ってもよいと考えるサービスを特定しています。
less-uncountable|The new lighting system uses _____ electricity than the old fluorescent lights.|less/fewer/fewest/least|新しい照明システムは、古い蛍光灯より消費電力が少なくなっています。
comparative-modifier|The second product demonstration was _____ more informative than the brief introduction we watched online.|much/very/most/many|2回目の商品実演は、オンラインで見た短い紹介よりずっと参考になりました。
double-as|The expanded dining area seats twice as many customers _____ the original room.|as/than/that/so|拡張後の食事スペースには、元の部屋の2倍の客が座れます。
both-determiner|_____ entrances to the building will remain open during the fire safety inspection.|Both/Either/Each/Another|消防検査中も、建物の二つの入口はどちらも開けておきます。
other-plural|Please place returned books on this cart and leave the _____ carts for new arrivals.|other/another/others/every|返却された本はこの台車に置き、ほかの台車は新着図書用に空けておいてください。
little-uncountable|Adding _____ information about parking would make the invitation more useful to visitors.|a little/a few/many/each|駐車場について少し情報を加えると、招待状は来訪者にとってさらに役立つものになります。
lexical-finance|The customer requested an itemized _____ showing the cost of each service before making payment.|invoice~invoice は請求内容と金額を示す請求書です。/itinerary~itinerary は旅程表です。/inventory~inventory は在庫一覧や棚卸しです。/interview~interview は面接や取材です。|顧客は支払い前に、各サービスの料金を示した明細付き請求書を求めました。|提供されたサービスごとの請求額を示す文書なので invoice を使います。
lexical-recruitment|Only applicants who meet the minimum _____ will be invited for an interview.|qualifications~qualifications は職務に必要な資格・適格性です。/destinations~destinations は目的地です。/advertisements~advertisements は広告です。/installations~installations は設置や設備です。|最低限の応募資格を満たす人だけが、面接に招かれます。|採用面接に進むために満たす条件なので qualifications が適切です。
lexical-delivery|The shipment was delayed because the address on the package was _____.|incomplete~incomplete は必要な情報がそろっていないことです。/affordable~affordable は無理なく買える価格であることです。/durable~durable は丈夫で長持ちすることです。/profitable~profitable は利益が出ることです。|荷物の住所の記載が不完全だったため、配送が遅れました。|住所の情報が不足して届けられなかった流れには incomplete が合います。
'''

DATA += r'''
noun-position|Thank you for your prompt _____ to our request for an updated price list.|response/responsive/responsively/respond|改訂版の価格表を求める当方の依頼に、迅速にご回答いただきありがとうございます。
adjective-position|An _____ description of the fault will help the technician identify the problem quickly.|accurate/accuracy/accurately/accurateness~accurateness は名詞で、description の性質を表す形容詞ではありません。|不具合を正確に説明すると、技術者が問題をすばやく特定する助けになります。
adverb-position|Make sure the shipping labels are _____ attached before the parcels leave the warehouse.|correctly/correct/correction/correctness~correctness は名詞で、取り付け方を修飾する副詞にはなりません。|荷物が倉庫を出る前に、配送ラベルが正しく貼られていることを確認してください。
preposition-gerund|Please do not change the delivery address without _____ the customer service team.|informing/inform/to inform/informed|顧客対応チームへ知らせずに配送先の住所を変更しないでください。
conditional-present|If the weather _____ clear this afternoon, the company's annual ceremony will be held in the garden.|remains/will remain/remained/remaining|今日の午後も晴天が続けば、会社の年次式典は庭園で行われます。
modal-passive|The confidential records must _____ in a secure cabinet when they are not being used.|be stored/store/stored/be storing|機密記録は使用していないとき、安全な戸棚に保管する必要があります。
uncountable-singular|The furniture in the guest rooms _____ regular inspection for signs of wear.|requires/require~require は複数主語に対応する形で、不可算名詞 furniture に合いません。/to require~to 不定詞だけではこの文の述語になりません。/requiring|客室の家具は、摩耗の兆候がないか定期的な点検が必要です。
gerund-subject|Reducing food waste in the staff cafeteria _____ the company money each month.|saves/save~動名詞句は単数扱いなので原形の save では一致しません。/to save~to 不定詞だけではこの文の述語になりません。/saving|社員食堂の食品廃棄を減らすことは、毎月会社の経費削減につながります。
number-plural|A number of customers _____ paper receipts even though digital copies are available.|request/requests~requests は単数形で、a number of customers に合いません。/to request~to 不定詞だけではこの文の述語になりません。/requesting|電子版を利用できるにもかかわらず、多くの顧客が紙の領収書を求めます。
subject-pronoun|Ms. Grant will lead the inspection because _____ has extensive experience with laboratory equipment.|she/her/hers~hers は所有物を指し、この文脈の人物自身を表せません。/herself~herself は再帰代名詞で、この位置で単独の主語にはなりません。|グラントさんは研究用機器の豊富な経験があるため、点検を指揮します。
independent-possessive|The reports on the upper shelf belong to our team; the reports on the lower shelf are _____.|theirs/their/they/them|上の棚の報告書は私たちのチームのもので、下の棚の報告書は彼らのものです。
one-substitute|This envelope is too small for the catalog; please ask the mailroom for a larger _____.|one/ones/it/them|この封筒はカタログを入れるには小さすぎます。郵便物担当室にもっと大きなものを頼んでください。
at-time|The security staff change shifts _____ midnight, when visitor access is already closed.|at/in/on/of|警備員は、来訪者の入館がすでに終了している深夜0時に交代します。
depend-on|Approval of the grant will depend _____ whether the project meets the program's research goals.|on/at/for/to|助成金の承認は、その事業がプログラムの研究目標に合致するかどうかで決まります。
within-period|Please return the completed evaluation form _____ seven days of finishing the course.|within/during/since/at|講座を終えてから7日以内に、記入済みの評価用紙を返送してください。
not-only-but|The new packaging is not only lighter _____ also easier for customers to open.|but/and/or/nor|新しい包装は軽量なだけでなく、顧客が開けやすくもなっています。
both-and|The position involves both preparing monthly forecasts _____ explaining them to department heads.|and/or/nor/but|その職務には、月次予測の作成と部門長への説明の両方が含まれます。
before-clause|Please verify the recipient's email address _____ you send any confidential attachments.|before/because of/during/despite|機密の添付ファイルを送る前に、受取人のメールアドレスを確認してください。
relative-time|The reservation system will show the days _____ the studio is available for private lessons.|when/which/who/whose|予約システムには、スタジオを個人レッスンに利用できる日が表示されます。|後続節の主要な文構造は the studio is available で完結しており、days を時の関係で補う when を使います。
fused-what|The customer service representative carefully noted _____ the caller said about the damaged goods.|what/that~that では後続節内で欠けている目的語を補えません。/who/whose|顧客対応担当者は、電話の相手が破損品について述べた内容を注意深く記録しました。
relative-prep-person|The editor to _____ the manuscript was sent is currently attending a conference overseas.|whom/who/that/whose|原稿を送付した相手の編集者は、現在海外の会議に出席しています。
less-uncountable|The revised installation procedure requires _____ time than the method described in the old manual.|less/fewer/fewest/least|改訂された設置手順は、古い説明書にある方法より所要時間が短くなっています。
correlative-comparison|The closer the hotel is to the station, the _____ it is for guests arriving by train.|easier/easy/easiest/easily|ホテルが駅に近ければ近いほど、列車で到着する宿泊客にとって利用しやすくなります。
as-positive|The replacement fabric is as _____ as the original material and can withstand frequent washing.|durable/more durable/most durable/durably|交換用の生地は元の素材と同じくらい丈夫で、頻繁な洗濯に耐えられます。
each-singular-noun|The inspection checklist must be completed for _____ vehicle before it leaves the depot.|each/many/several/all|車庫を出る前に、各車両について点検表を記入し終える必要があります。
article-an|The board hired _____ independent consultant to review the company's purchasing procedures.|an/a/many/these|理事会は会社の購買手続きを点検するため、独立したコンサルタントを雇いました。
all-of-plural|_____ of the participants received a certificate after completing the practical assessment.|All/Every/Another/Much|実技評価を終えた後、参加者全員が修了証を受け取りました。
lexical-communication|The instructions were unclear, so we asked the supplier to _____ the assembly procedure.|clarify~clarify は不明な点を明確に説明する意味です。/decorate~decorate は飾る意味です。/transport~transport は物や人を運ぶ意味です。/recycle~recycle は再生利用する意味です。|説明が不明確だったため、供給業者に組み立て手順を明確に説明してもらうよう依頼しました。|説明の不明点を解消してもらうので clarify が適切です。
lexical-maintenance|The technician marked the power cord as _____ because its protective covering was torn.|defective~defective は欠陥があり正常に使えない状態です。/confidential~confidential は機密のという意味です。/optional~optional は任意のという意味です。/seasonal~seasonal は季節的なという意味です。|保護被覆が破れていたため、技術者はその電源コードを不良品と表示しました。|被覆の破損は製品の不具合なので defective が合います。
lexical-compliance|Attendance at the safety briefing is _____; employees who miss it must attend a make-up session.|mandatory~mandatory は義務であることです。/optional~optional は任意であり、欠席者も受講が必須という後半に矛盾します。/incidental~incidental は付随的なという意味で、受講義務を表しません。/provisional~provisional は暫定的なという意味で、受講義務を表しません。|安全説明会への出席は義務であり、欠席した従業員は補講に出席する必要があります。|欠席しても補講の出席が必要なため、参加は mandatory です。
'''

DATA += r'''
noun-position|We appreciate your _____ while our staff investigate the cause of the service interruption.|cooperation/cooperative/cooperatively/cooperate|サービス中断の原因をスタッフが調べる間、ご協力いただきありがとうございます。
adjective-position|The report provides an unusually _____ description of conditions inside the storage container.|accurate/accuracy/accurately/accurateness~accurateness は名詞で、この程度の副詞の後に置く形容詞ではありません。|その報告書は、保管容器内の状態を非常に正確に説明しています。
linking-adjective|The vegetables should remain _____ for several days if they are kept in the refrigerator.|fresh/freshly/freshness/freshen|冷蔵庫に入れておけば、野菜は数日間新鮮な状態を保つはずです。
past-specific|The branch manager _____ the revised opening hours at yesterday's staff meeting.|announced/announces/will announce/has announced|支店長は昨日の職員会議で、変更後の営業時間を発表しました。
infinitive-complement|The company plans _____ its customer service center closer to the main railway station.|to relocate/relocating/relocated/relocation|会社は顧客サービスセンターを主要鉄道駅のもっと近くへ移転する予定です。
past-perfect|By the time production resumed, the technician _____ the faulty temperature sensor.|had replaced/has replaced/will replace/replacing|生産が再開するまでに、技術者は故障した温度センサーを交換していました。
neither-singular|Neither of the suggested solutions _____ suitable for a building of this age.|is/to be/be/being|提案された二つの解決策は、どちらもこの築年数の建物には適していません。
one-of-singular|One of the local banks _____ small businesses free advice on managing cash flow.|offers/offer~offer は複数主語に対応する形で、主語の one に一致しません。/to offer~to 不定詞だけではこの文の述語になりません。/offering|地元の銀行の一つは、小規模企業に資金繰り管理の無料相談を提供しています。
there-plural|There _____ several devices in this laboratory that require a separate power supply.|are/is/be/being|この研究室には、別系統の電源を必要とする装置がいくつかあります。
possessive-determiner|The company has revised _____ policy on working from home to give employees more flexibility.|its/it/itself~itself は再帰代名詞なので policy の前で所有を表せません。/it's~it's は it is または it has の短縮形で、所有格ではありません。|会社は従業員がより柔軟に働けるよう、在宅勤務に関する方針を改訂しました。
subject-pronoun|The employees have reviewed the new procedure, and _____ are ready to begin the trial.|they/them/their/theirs|従業員たちは新しい手順を確認し、試行を始める準備ができています。
reflexive-object|Ms. Reed congratulated _____ on completing the difficult task ahead of schedule.|herself/myself~myself は一人称単数で、三人称の Ms. Reed に一致しません。/ourselves~ourselves は一人称複数で、三人称単数の Ms. Reed に一致しません。/itself~itself は物事を表すため、人物の Ms. Reed に合いません。|リードさんは、難しい仕事を予定より早く終えたことを自分で喜びました。
in-month|The factory will close for its annual equipment inspection _____ August.|in/on/at/of|工場は8月、年に1度の設備点検のため休業します。
responsible-for|The regional director is responsible _____ approving all contracts above the specified value.|for/to/at/with|地域統括責任者は、指定額を超えるすべての契約を承認する責任を負っています。
despite-noun|The temporary signs remained in place _____ the strong wind throughout the night.|despite/although/because/unless|一晩中強い風が吹いたにもかかわらず、仮設の標識はその場に立っていました。
purpose-so-that|The engineers added a viewing window _____ operators could inspect the process without opening the cover.|so that/so as to/because of/despite~despite は前置詞で、主語＋動詞の節を直接続けられません。|カバーを開けずに工程を確認できるよう、技術者たちは観察窓を追加しました。
either-or|Customers may pay either in advance _____ upon collection of the goods.|or/and/nor/but|顧客は、前払いか商品の受け取り時に支払いができます。
while-clause|Please keep the passage clear _____ visitors are moving between the exhibition rooms.|while/during/despite/because of|来訪者が展示室の間を移動している間は、通路をふさがないでください。
relative-possessive|The publisher is looking for authors _____ books appeal to readers interested in local history.|whose/who/whom/which|出版社は、郷土史に関心を持つ読者に訴える本を書く著者を探しています。
relative-person-subject|Any employee _____ notices an unusual smell near the storage tanks should notify the supervisor.|who/whom/whose/which|貯蔵タンクの近くで異臭に気づいた従業員は、監督者に知らせてください。
relative-thing-subject|The entrance ramp, _____ was added during the renovation, makes the building more accessible.|which/who/where/whose|改修時に追加された入口のスロープにより、建物を利用しやすくなりました。
fewer-countable|The online form has _____ questions than the printed version, but it collects the same essential information.|fewer/less/little/least|オンラインの用紙は印刷版より質問が少ないものの、同じ必須情報を集められます。
comparative-than|The coastal route is _____ than the inland road, especially after heavy rain.|more dangerous/dangerous/most dangerous/dangerously|沿岸の経路は内陸の道より危険で、特に大雨の後は危険性が高まります。
superlative-range|Of the five apartments we visited, the one nearest the station was the _____.|most expensive/expense~expense は名詞で、ここで必要な価格の程度の補語には合いません。/more expensive/expensively|見学した5軒のアパートの中で、駅に最も近い物件が最も高額でした。
much-uncountable|We do not have _____ information about the proposed merger, so no decision can be made yet.|much/many/a few/several|提案されている合併についての情報があまりないため、まだ決定はできません。
few-countable|The auditor asked to see _____ receipts from each month to verify the expense records.|a few/a little/much/each|監査人は経費の記録を確認するため、各月の領収書を何枚か見たいと求めました。
another-singular|The training room is occupied until noon; can we reserve _____ room for the morning interviews?|another/other/others/every|研修室は正午まで使用中です。午前の面接用に別の部屋を予約できますか。
lexical-inventory|A _____ of qualified drivers has forced the delivery company to reduce its weekend service.|shortage~shortage は必要な数に足りないことです。/surplus~surplus は余剰で、運転手不足による減便とは逆の意味です。/collection~collection は収集物や集める行為で、人員不足を表しません。/reservation~reservation は予約で、人員不足を表しません。|資格を持つ運転手の不足により、その配送会社は週末のサービスを減らさざるを得なくなりました。|運転手が足りないためサービスを縮小したので shortage が適切です。
lexical-reservation|The hotel had no _____ rooms, so the receptionist suggested another property nearby.|vacant~vacant は部屋が空いていることを表します。/fluent~fluent は言語などに流暢であることです。/loyal~loyal は忠実なという意味です。/portable~portable は持ち運びできるという意味で、客室の空き状況を表せません。|そのホテルには空室がなかったため、受付係は近くの別の宿泊施設を勧めました。|別のホテルを案内したのは空室がないためなので vacant rooms を使います。
lexical-evaluation|Price is one of several _____ the committee will use to select the winning proposal.|criteria~criteria は判断や選定の基準の複数形です。/corridors~corridors は廊下の複数形です。/currencies~currencies は通貨の複数形です。/containers~containers は容器の複数形です。|価格は、委員会が採用する提案を選ぶ際に使う複数の基準の一つです。|価格のような比較・選定の基準は criteria です。
'''

DATA += r'''
adverb-position|The new billing system calculates the total on each invoice more _____ than the manual process did.|accurately/accurate/accuracy/accurateness~accurateness は名詞で、動作の程度や方法を修飾する副詞にはなりません。|新しい請求システムは、手作業よりも正確に各請求書の合計を計算します。
participle-cause|The walking tour was _____, so several visitors rested at the cafe before returning to their hotel.|exhausting/exhausted/exhaustion/exhaust|徒歩ツアーは疲れるものだったので、何人かの来訪者はホテルに戻る前にカフェで休みました。
participle-feeling|The guests were _____ with the service and wrote a positive review of the restaurant.|satisfied/satisfying/satisfaction/satisfy|客はサービスに満足し、そのレストランの好意的な口コミを書きました。
preposition-gerund|Thank you for _____ to our survey before the closing date.|responding/respond/to respond/responded|締め切りまでに当社のアンケートにご回答いただき、ありがとうございます。
future-progressive|At this time next week, the inspection team _____ the supports underneath the bridge.|will be examining/were examining/have examined/had examined|来週の今頃、点検チームは橋の下の支柱を調べているでしょう。
conditional-present|If the shipment _____ the airport before six, it will be loaded onto the evening flight.|reaches/will reach/reached/reaching|発送品が6時までに空港へ到着すれば、夜の便に積み込まれます。
uncountable-singular|The research presented in these reports _____ that customers prefer shorter waiting times.|indicates/indicate~indicate は複数主語に対応する現在形で、不可算名詞 research に一致しません。/to indicate~to 不定詞だけではこの文の述語になりません。/indicating|これらの報告書に示された研究は、顧客がより短い待ち時間を好むことを示しています。
head-singular|The number of visitors to the museum _____ increased since the new exhibition opened.|has/have~主語の中心は単数の number なので have では一致しません。/to have~to 不定詞だけではこの文の述語になりません。/having|新しい展示の開始以来、博物館の来館者数が増えています。
gerund-subject|Reading the warning labels before using unfamiliar equipment _____ many avoidable accidents.|prevents/prevent~動名詞句は単数扱いなので prevent では一致しません。/to prevent~to 不定詞だけではこの文の述語になりません。/preventing|不慣れな機器を使う前に警告ラベルを読むことは、多くの防げる事故の防止につながります。
object-pronoun|When the manager returns from lunch, please give _____ the revised seating plan.|him/he/his/himself~命令文の主語である you と相手の manager は別人なので再帰代名詞は使いません。|部長が昼食から戻ったら、修正した座席配置図を彼に渡してください。
independent-possessive|The document on the left is mine; is the document on the right _____?|yours/your/you~you は人物を表すため、所有物を尋ねるこの補語に合いません。/yourself~yourself は人物自身を表し、書類の所有者との関係を示せません。|左の書類は私のものです。右の書類はあなたのものですか。
those-substitute|Prices at the temporary shop are identical to _____ listed in the online catalog.|those/that/it/its|仮設店舗の価格は、オンラインカタログに記載された価格と同じです。
at-time|The airport information desk opens _____ five each morning, before the first departures.|at/in/on/of|空港の案内所は、始発便の出発前の毎朝5時に開きます。
within-period|Our customer service team aims to respond to every complaint _____ two business days.|within/during/since/at|顧客対応チームは、すべての苦情に2営業日以内に対応することを目指しています。
depend-on|The success of the exhibition will depend _____ careful coordination among all participating organizations.|on/at/for/to|展示会の成功は、参加するすべての団体の入念な連携にかかっています。
not-only-but|The new production method not only reduces waste _____ also improves the durability of the final product.|but/and/or/nor|新しい製造方法は、廃棄物を減らすだけでなく完成品の耐久性も高めます。
because-clause|The reimbursement request was returned _____ several required receipts were missing.|because/because of/despite/unless|必要な領収書が何枚か不足していたため、経費の払い戻し申請は返却されました。
purpose-so-that|The technician labeled each cable _____ the next shift could reconnect the equipment without confusion.|so that/so as to/because of/despite~despite は前置詞で、主語＋動詞の節を直接続けられません。|次の勤務の担当者が混乱せず機器を再接続できるよう、技術者は各ケーブルにラベルを付けました。
relative-prep-person|The consultant about _____ you asked has extensive experience in improving hospital workflows.|whom/who/that/whose|あなたがお尋ねになったコンサルタントは、病院の業務手順の改善に豊富な経験があります。
relative-prep-thing|The room in _____ the equipment is stored must be kept at a constant temperature.|which/that/who/where|機器が保管されている部屋は、一定の温度に保つ必要があります。
relative-time|The notice lists the hours _____ the warehouse accepts deliveries from outside suppliers.|when/which/who/whose|掲示には、倉庫が外部の供給業者からの配達を受け付ける時間が記載されています。
less-uncountable|The updated packaging uses _____ material than the previous design while providing the same protection.|less/fewer/fewest/least|改良された包装は、同じ保護性能を保ちながら、以前の設計より使用する材料が少なくなっています。
comparative-modifier|After the software upgrade, the reservation system responded _____ more quickly than it had before.|much/very/most/many|ソフトウェア更新後、予約システムの応答は以前よりずっと速くなりました。
better-of-two|The committee considered two options and identified the _____ of the two after examining their costs.|better/best/good/well|委員会は二つの選択肢を検討し、費用を調べてからよりよいほうを特定しました。
both-determiner|_____ components must be replaced together because they were designed to work as a pair.|Both/Either/Each/Another|その二つの部品は対になって動作するように設計されているため、両方を一緒に交換する必要があります。
other-plural|Employees who cannot attend on Thursday may choose from the _____ sessions listed in the email.|other/another/others/every|木曜日に出席できない従業員は、メールに記載されたほかの回から選べます。
article-an|The manufacturer sent _____ engineer to investigate why the machine had stopped unexpectedly.|an/a/many/these|メーカーは機械が突然停止した理由を調査するため、技術者を1人派遣しました。
lexical-negotiation|Both sides made concessions during the talks and eventually reached a _____ on the delivery terms.|compromise~compromise は双方が譲歩してまとまる妥協です。/forecast~forecast は予測です。/receipt~receipt は領収書や受領です。/renovation~renovation は建物などの改修です。|交渉中に両者が譲歩し、最終的に配送条件について妥協に達しました。|双方の譲歩で条件がまとまるため compromise が適切です。
lexical-quantity|Do not exceed the maximum carrying _____ of this pallet when stacking heavy cartons.|capacity~capacity は受け入れたり支えたりできる最大量を表します。/currency~currency は通貨です。/humidity~humidity は湿度です。/frequency~frequency は頻度です。|重い箱を積み重ねる際は、このパレットの最大積載能力を超えないでください。|パレットが支えられる荷物の上限なので carrying capacity を使います。
lexical-location|The company plans to _____ to a larger office because its current workspace is too crowded.|relocate~relocate は所在地を移すことです。/reimburse~reimburse は立て替え費用を払い戻すことです。/renovate~renovate は建物を改修することで、to a larger office の移転先を取る用法ではありません。/remind~remind は思い出させることです。|現在の作業場所が手狭なため、会社はもっと大きな事務所へ移転する予定です。|手狭な事務所から別の大きな事務所へ移るので relocate が自然です。
'''

VERSIONS = {1: 2, 11: 3, 18: 2, 23: 2, 32: 2}

LINKS = """
approval-1 provide-1 reserve-1 replace-1 approve-1 work-1 receive-1 offer-1 available-1 keep-2 introduce-1 contact-1 submit-1 store-1 interest-1 auditorium-1 receive-1 follow-1 join-1 scanner-1 invite-1 budget-1 select-1 reliable-1 space-1 send-1 book-1 approve-1 postpone-1 replace-1
membership-1 customer-1 company-1 engineer-1 gallery-1 company-1 contract-1 information-1 product-1 company-1 technician-1 suitcase-1 public-2 airport-1 equipment-1 road-1 machine-1 tour-1 guest-1 technician-1 architect-1 system-1 form-1 reserve-1 employee-1 guest-1 entrance-1 receipt-1 nurse-1 check-1
manager-1 employee-1 receptionist-1 customer-1 museum-1 manager-1 screen-1 room-1 convenient-1 rate-1 laptop-1 itinerary-1 supervisor-1 revise-1 service-1 customer-1 explain-1 attend-1 account-1 request-1 volunteer-1 battery-1 camera-1 furniture-1 museum-1 document-1 road-1 email-1 elevator-1 regulation-1
requirement-1 password-1 instruction-1 bakery-1 research-1 exit-1 invoice-1 room-1 passenger-1 volunteer-1 submit-1 refrigerator-1 company-1 borrow-1 meal-1 refund-1 machine-1 guide-1 subscription-1 route-1 rent-1 room-1 printer-1 hotel-1 technician-1 microphone-1 transit-1 shelf-1 room-1 committee-1
spend-1 guide-1 audit-1 hotel-1 reduce-1 guest-1 invoice-1 equipment-1 visitor-1 company-1 director-1 requirement-1 auditorium-1 demand-1 agreement-1 entrance-1 software-1 receipt-1 large-1 order-1 warranty-1 highway-1 branch-1 option-1 move-1 presentation-1 editor-1 discount-1 demand-1 restaurant-1
customer-1 architect-1 invoice-1 complete-1 code-1 supervisor-1 service-1 applicant-1 key-1 committee-1 desk-1 department-1 arrange-1 traffic-1 ferry-1 designer-1 computer-1 sign-1 technician-1 employee-1 company-1 map-1 prepare-1 storage-1 elevator-1 branch-1 parking-1 owner-1 auditor-1 battery-1
theater-1 form-1 volunteer-1 trade-1 motor-1 survey-1 quality-1 instructor-1 cabinet-1 assistant-1 guide-1 instruction-1 bus-1 import-1 customer-1 facility-1 manager-1 system-1 translator-1 room-1 service-1 system-1 product-1 customer-1 entrance-1 book-2 parking-1 customer-1 applicant-1 address-1
price-1 technician-1 parcel-1 address-1 company-1 record-1 furniture-1 waste-1 customer-1 equipment-1 shelf-1 catalog-1 security-1 research-1 form-1 customer-1 department-1 email-1 system-1 customer-1 editor-1 procedure-1 hotel-1 material-1 vehicle-1 board-1 complete-1 instruction-1 technician-1 employee-1
staff-1 accurate-1 refrigerator-1 manager-1 company-1 technician-1 solution-1 bank-1 device-1 company-1 employee-1 task-1 factory-1 director-1 wind-1 engineer-1 customer-1 visitor-1 author-1 employee-1 building-1 form-1 route-1 expensive-1 information-1 receipt-1 room-1 shortage-1 room-1 proposal-1
invoice-1 tour-1 service-1 survey-1 bridge-1 shipment-1 research-1 visitor-1 label-1 manager-1 document-1 price-1 airport-1 complaint-1 success-1 product-1 receipt-1 technician-1 consultant-1 equipment-1 warehouse-1 material-1 system-1 committee-1 component-1 employee-1 engineer-1 delivery-1 pallet-1 company-1
""".split()

def generate(from_batch=1, links_only=False):
    rows = [line.split('|') for line in DATA.strip().splitlines() if line.strip()]
    assert len(rows) % 30 == 0, len(rows)
    answer_positions = []
    for batch in range(len(rows) // 30):
        positions = [(i + batch * 2) % 4 for i in range(30)]
        random.Random(814 + batch).shuffle(positions)
        answer_positions.extend(positions)
    sense_ids = {sense['id'] for path in (ROOT/'content/batches').glob('vocab-*.json') for word in json.loads(path.read_text())['items'] for sense in word['senses']}
    all_items = []
    for i, row in enumerate(rows):
        fam, stem, raw_options, translation, *custom = row
        skill, explanation, notes = FAMILIES[fam]
        explanation = custom[0] if custom else explanation
        options = raw_options.split('/')
        assert len(options) == 4, row
        parsed = [option.split('~', 1) for option in options]
        texts = [part[0] for part in parsed]
        details = [part[1] if len(part) == 2 else (explanation if j == 0 else notes[j-1]) for j, part in enumerate(parsed)]
        order = [1, 2, 3]
        random.Random(i + 431).shuffle(order)
        order.insert(answer_positions[i], 0)
        ids = 'abcd'
        item = dict(id=f'q-{i+1:04}', version=VERSIONS.get(i+1, 1), type='part5', stem=stem,
                    options=[dict(id=ids[j], text=texts[k]) for j, k in enumerate(order)],
                    answerId=ids[order.index(0)], translationJa=translation, explanationJa=explanation,
                    optionExplanations={ids[j]: f'「{texts[k]}」: {details[k]}' for j, k in enumerate(order)},
                    skillId=skill, secondarySkillIds=[], vocabularySenseIds=[f'v-{LINKS[i]}'] if i < len(LINKS) and f'v-{LINKS[i]}' in sense_ids else [],
                    difficulty='standard', familyId=fam, sourceIds=['iibc-format'], reviewStatus='pending')
        all_items.append(item)
    for offset in range(0, len(all_items), 30):
        if offset // 30 + 1 < from_batch:
            continue
        items = all_items[offset:offset+30]
        for skill in ('pos','verb','agreement','pronoun','preposition','conjunction','relative','comparison','determiner','vocabulary'):
            assert sum(q['skillId'] == skill for q in items) == 3, (offset, skill)
        batch_id = f'questions-{offset//30+1:03}'
        batch = dict(id=batch_id, schemaVersion=1, createdAt='2026-10-04T00:00:00Z',
                     author='question_author', model=None, input='research policy v1; independent original authoring',
                     status='generated', items=items)
        path = ROOT / 'content/batches' / f'{batch_id}.json'
        if path.exists():
            old_by_id = {q['id']:q for q in json.loads(path.read_text())['items']}
            for item in items:
                old = old_by_id.get(item['id'])
                if old:
                    clean = lambda value: {k:v for k,v in value.items() if k not in ('version','reviewStatus')}
                    item['version'] = max(item['version'], old['version'] + int(clean(old) != clean(item)))
        if links_only:
            existing = json.loads(path.read_text())
            for previous, generated in zip(existing['items'], items):
                assert previous['id'] == generated['id']
                previous['vocabularySenseIds'] = generated['vocabularySenseIds']
                previous['version'] = generated['version']
            batch = existing
        path.write_text(json.dumps(batch, ensure_ascii=False, indent=2)+'\n')
        if not links_only:
            blind_dir = ROOT / 'content/blind'
            blind_dir.mkdir(exist_ok=True)
            blind = dict(id=batch_id, items=[{key:q[key] for key in ('id','version','stem','options')} for q in items])
            (blind_dir / f'{batch_id}.json').write_text(json.dumps(blind, ensure_ascii=False, indent=2)+'\n')
    print(f'Wrote {len(all_items)} original questions in {len(all_items)//30} batches (pending review).')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--from-batch', type=int, default=1)
    parser.add_argument('--links-only', action='store_true')
    args = parser.parse_args()
    generate(args.from_batch, args.links_only)
