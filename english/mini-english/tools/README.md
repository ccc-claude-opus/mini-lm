# tools

`count_1w.txt`（Google Web Trillion Word Corpus 的前 333,333 個高頻詞與次數）**沒有放進版本庫**（約 5 MB）。
需要的時候下載：

```bash
curl -sL -o tools/count_1w.txt https://norvig.com/ngrams/count_1w.txt
```

用途：

* `data/lexicon_part*.tsv` 的選詞參考；
* `report.md` §6.5 的 token／字型命中率；
* `data/coverage_sample.txt` 的抽樣母體（Google 10,000 常用英文詞表的前 3,000 個）。

`coverage_sample.txt` 與 `coverage.tsv` 已經把抽樣結果固定下來，所以就算沒有這個檔案，
覆蓋率測試仍然可以重跑（`python check.py --lexicon` 不需要它）。
