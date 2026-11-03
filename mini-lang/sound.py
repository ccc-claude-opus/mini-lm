"""Mini-Lang 的音寫（反切）：用 256 字寫出任何中文音節。

每個音節分成「聲母」與「韻母」。字表中有同音字就直接用那個字；
沒有的話用兩個字「反切」：取第一字的聲母、第二字的韻母與聲調。

用法：
    python sound.py                       # 檢查字表的聲母、韻母覆蓋率
    python sound.py wang2 xiao3 ming2     # 音寫：輸入拼音（數字標調，ü 寫成 v，輕聲 5）
"""
import re
import sys

# 256 字的讀音（拼音，數字標調；輕聲為 5）
READINGS = '''
我 wo3 你 ni3 他 ta1 們 men5 這 zhe4 那 na4 誰 shei2 什 shen2 麼 me5 哪 na3 怎 zen3 樣 yang4 自 zi4 己 ji3 每 mei3
的 de5 了 le5 過 guo4 嗎 ma5 呢 ne5 吧 ba5 不 bu4 沒 mei2 是 shi4 有 you3 在 zai4 和 he2 也 ye3 都 dou1 很 hen3
太 tai4 最 zui4 更 geng4 還 hai2 就 jiu4 再 zai4 會 hui4 能 neng2 要 yao4 可 ke3 以 yi3 得 de2 給 gei3 對 dui4
跟 gen1 從 cong2 到 dao4 為 wei4 因 yin1 所 suo3 如 ru2 果 guo3 但 dan4 只 zhi3 起 qi3 比 bi3
一 yi1 二 er4 三 san1 四 si4 五 wu3 六 liu4 七 qi1 八 ba1 九 jiu3 十 shi2 百 bai3 千 qian1 萬 wan4 兩 liang3
幾 ji3 半 ban4 第 di4 個 ge4 些 xie1 次 ci4 點 dian3 塊 kuai4 歲 sui4
年 nian2 月 yue4 日 ri4 天 tian1 時 shi2 候 hou4 今 jin1 明 ming2 昨 zuo2 早 zao3 晚 wan3 午 wu3 現 xian4 分 fen1
鐘 zhong1 週 zhou1 先 xian1
上 shang4 下 xia4 左 zuo3 右 you4 前 qian2 後 hou4 裡 li3 外 wai4 中 zhong1 間 jian1 東 dong1 西 xi1 南 nan2
北 bei3 邊 bian1 方 fang1 地 di4
來 lai2 去 qu4 走 zou3 坐 zuo4 站 zhan4 住 zhu4 回 hui2 進 jin4 出 chu1 開 kai1 關 guan1 拿 na2 放 fang4 用 yong4
做 zuo4 作 zuo4 說 shuo1 話 hua4 聽 ting1 看 kan4 見 jian4 寫 xie3 學 xue2 習 xi2 教 jiao1 問 wen4 叫 jiao4
想 xiang3 知 zhi1 道 dao4 懂 dong3 記 ji4 覺 jue2 喜 xi3 歡 huan1 愛 ai4 吃 chi1 喝 he1 睡 shui4 買 mai3 賣 mai4
找 zhao3 等 deng3 幫 bang1 穿 chuan1 洗 xi3 玩 wan2 打 da3 生 sheng1 完 wan2
大 da4 小 xiao3 多 duo1 少 shao3 長 chang2 短 duan3 高 gao1 老 lao3 好 hao3 壞 huai4 新 xin1 快 kuai4 慢 man4
冷 leng3 熱 re4 難 nan2 容 rong2 易 yi4 真 zhen1 忙 mang2 病 bing4 重 zhong4 遠 yuan3 近 jin4 白 bai2 黑 hei1
紅 hong2 色 se4 樂 le4 貴 gui4
人 ren2 男 nan2 女 nv3 子 zi3 孩 hai2 爸 ba4 媽 ma1 哥 ge1 姐 jie3 弟 di4 妹 mei4 朋 peng2 友 you3 師 shi1
家 jia1 名 ming2 字 zi4 身 shen1 體 ti3 頭 tou2 手 shou3 眼 yan3 口 kou3 心 xin1 水 shui3 火 huo3 山 shan1
雨 yu3 氣 qi4 電 dian4 車 che1 路 lu4 門 men2 房 fang2 書 shu1 衣 yi1 服 fu2 錢 qian2 飯 fan4 菜 cai4 茶 cha2
肉 rou4 花 hua1 校 xiao4 醫 yi1 店 dian4 國 guo2 文 wen2 語 yu3 言 yan2 事 shi4 情 qing2 題 ti2 工 gong1
腦 nao3 機 ji1 飛 fei1 意 yi4 思 si1
請 qing3 謝 xie4 迎 ying2 係 xi4
'''
PINYIN = dict(re.findall(r'(\S) ([a-zv]+[1-5])', READINGS))

INITIALS = ['zh', 'ch', 'sh', 'b', 'p', 'm', 'f', 'd', 't', 'n', 'l', 'g', 'k', 'h',
            'j', 'q', 'x', 'r', 'z', 'c', 's']
# 普通話的全部韻母（y、w 開頭的音節還原成零聲母 + 介音韻母）
FINALS = ['a', 'o', 'e', 'er', 'ai', 'ei', 'ao', 'ou', 'an', 'en', 'ang', 'eng', 'ong', '-i',
          'i', 'ia', 'ie', 'iao', 'iu', 'ian', 'in', 'iang', 'ing', 'iong',
          'u', 'ua', 'uo', 'uai', 'ui', 'uan', 'un', 'uang', 'ueng',
          'v', 've', 'van', 'vn']
# 反切第一字：每個聲母固定用一個代表字（韻母單純、常用），音寫才穩定好讀
INITIAL_CHAR = {'b': '不', 'p': '朋', 'm': '媽', 'f': '分', 'd': '大', 't': '他', 'n': '你', 'l': '了',
                'g': '個', 'k': '可', 'h': '和', 'j': '幾', 'q': '七', 'x': '西', 'zh': '這', 'ch': '吃',
                'sh': '是', 'r': '日', 'z': '子', 'c': '次', 's': '四', '': '愛'}
# 字表裡沒有的韻母，用最接近的韻母代替（音寫只求聽得出來）
NEAREST = {'o': 'uo', 'uang': 'ang', 'ueng': 'eng', 'vn': 'in'}

def split(syl):
    """'wang2' → ('', 'uang', 2)；'zhi1' → ('zh', '-i', 1)。"""
    m = re.fullmatch(r'([a-zv]+)([1-5])', syl)
    if not m:
        raise ValueError(f'拼音格式錯誤: {syl}')
    s, tone = m.group(1), int(m.group(2))
    ini = next((i for i in INITIALS if s.startswith(i)), '')
    fin = s[len(ini):]
    if not ini:  # y、w 開頭：零聲母
        fin = {'yi': 'i', 'yin': 'in', 'ying': 'ing', 'wu': 'u', 'yu': 'v', 'yue': 've',
               'yuan': 'van', 'yun': 'vn', 'you': 'iu', 'yong': 'iong'}.get(s, fin)
        if s.startswith('y') and fin == s:
            fin = 'i' + s[1:]
        elif s.startswith('w') and fin == s:
            fin = 'u' + s[1:]
        fin = {'uei': 'ui', 'uen': 'un'}.get(fin, fin)
    elif ini in ('j', 'q', 'x') and fin.startswith('u'):
        fin = 'v' + fin[1:]  # ju、que、xuan 的 u 是 ü
    if fin == 'i' and ini in ('zh', 'ch', 'sh', 'r', 'z', 'c', 's'):
        fin = '-i'
    return ini, fin, tone

def table():
    """回傳 {聲母: [字]}、{韻母: [字]}、{(聲母, 韻母): [字]}。"""
    by_ini, by_fin, by_syl = {}, {}, {}
    for c, p in PINYIN.items():
        ini, fin, tone = split(p)
        by_ini.setdefault(ini, []).append(c)
        by_fin.setdefault(fin, []).append((c, tone))
        by_syl.setdefault((ini, fin), []).append((c, tone))
    return by_ini, by_fin, by_syl

def spell(syl):
    """把一個拼音音節寫成 1 個字（同音）或 2 個字（反切）。"""
    by_ini, by_fin, by_syl = table()
    ini, fin, tone = split(syl)
    if (ini, fin) in by_syl:  # 同音字，聲調最接近的優先
        return min(by_syl[(ini, fin)], key=lambda ct: ct[1] != tone)[0]
    fin = fin if fin in by_fin else NEAREST[fin]
    first = INITIAL_CHAR[ini]
    second = min(by_fin[fin], key=lambda ct: ct[1] != tone)[0]
    return first + second

def transcribe(syllables):
    """一個詞的音寫：每個音節之間用「·」隔開，整個放在〔〕裡。"""
    return '〔' + '·'.join(spell(s) for s in syllables) + '〕'

def main():
    if len(sys.argv) > 1:
        print(transcribe(" ".join(sys.argv[1:]).split()))
        return 0
    by_ini, by_fin, by_syl = table()
    print(f'讀音表 {len(PINYIN)} 字，不同的音節（不計聲調）{len(by_syl)} 個')
    missing_ini = [i for i in INITIALS + [''] if i not in by_ini]
    print('聲母:', '、'.join(f"{i or '零'}({by_ini[i][0]})" for i in INITIALS + [''] if i in by_ini))
    print('缺少的聲母:', missing_ini or '無')
    assert all(split(PINYIN[c])[0] == i for i, c in INITIAL_CHAR.items()), '代表字的聲母不對'
    print('韻母:', '、'.join(f'{f}({by_fin[f][0][0]})' for f in FINALS if f in by_fin))
    missing = [f for f in FINALS if f not in by_fin]
    print('缺少的韻母:', '、'.join(f'{f}→{NEAREST.get(f, "？")}' for f in missing) or '無')
    tones = sum(len({t for _, t in by_fin[f]}) for f in by_fin)
    print(f'韻母 × 聲調：{tones} / {len(by_fin) * 4} 種有字可用（反切時聲調以第二字為準）')
    return 1 if missing_ini or any(f not in NEAREST for f in missing) else 0

if __name__ == '__main__':
    sys.exit(main())
