# textgrid-parser

This repository is created for parsing and converting `.textgrid` files into `.json` files.To run this code, you should modify the path of input and output files in `parse.sh`:
`python parse_textgrid.py --input ./data/test.textgrid --output ./result/test.json
`

Sample input:
```
File type = "ooTextFile"
Object class = "TextGrid"

xmin = 0 
xmax = 2045.144149659864
tiers? <exists> 
size = 2 
item []: 
    item [1]:
        class = "IntervalTier" 
        name = "utterances" 
        xmin = 0 
        xmax = 2045.144149659864 
        intervals: size = 5 
        intervals [1]:
            xmin = 0 
            xmax = 2041.4217474125382 
            text = "" 
        intervals [2]:
            xmin = 2041.4217474125382 
            xmax = 2041.968276643991 
            text = "this" 
        intervals [3]:
            xmin = 2041.968276643991 
            xmax = 2042.5281632653062 
            text = "is" 
        intervals [4]:
            xmin = 2042.5281632653062 
            xmax = 2044.0487352585324 
            text = "a" 
        intervals [5]:
            xmin = 2044.0487352585324 
            xmax = 2045.144149659864 
            text = "demo" 
    item [2]:
        class = "IntervalTier" 
        name = "phones" 
        xmin = 0 
        xmax = 2045.144149659864
        intervals: size = 12
        intervals [1]:
            xmin = 0 
            xmax = 2041.4217474125382 
            text = "刚才我们看到短片当中介绍的年轻人啊" 
        intervals [2]:
            xmin = 2041.4217474125382 
            xmax = 2041.5438290324326 
            text = "就是我们今天的嘉宾"
        intervals [3]:
            xmin = 2041.5438290324326
            xmax = 2041.7321032910372
            text = "嗯很多人已经介绍过他了"
        intervals [4]:
            xmin = 2041.7321032910372            
            xmax = 2041.968276643991 
            text = "什么天才呀" 
        intervals [5]:
            xmin = 2041.968276643991 
            xmax = 2042.232189031843
            text = "曾经是神童之类这样的词语"
        intervals [6]:
            xmin = 2042.232189031843
            xmax = 2042.5281632653062 
            text = "嗯他的确是一个非常有才华的青年演奏家" 
        intervals [7]:
            xmin = 2042.5281632653062 
            xmax = 2044.0487352585324 
            text = "如今已经是个青年人了" 
        intervals [8]:
            xmin = 2044.0487352585324 
            xmax = 2044.2487352585324
            text = "曾经是个很可爱的小神童"
        intervals [9]:
            xmin = 2044.2487352585324
            xmax = 2044.3102321849011
            text = "这样我们掌声有请李传韵"
        intervals [10]:
            xmin = 2044.3102321849011
            xmax = 2044.5748932104329
            text = "主持人，主持人好"
        intervals [11]:
            xmin = 2044.5748932104329
            xmax = 2044.8329108578437
            text = "我必须要先说一些，李传韵特别特别紧张。"
        intervals [12]:
            xmin = 2044.8329108578437
            xmax = 2045.144149659864 
            text = "嗯" 
```

Sample output:
```
{
  "file_type": "ooTextFile", 
  "xmin": "0", 
  "xmax": "2045.144149659864", 
  "size": 2, 
  "tiers": [
    {
      "idx": "1", 
      "class": "IntervalTier", 
      "name": "utterances", 
      "xmin": "0", 
      "xmax": "2045.144149659864", 
      "size": "5", 
      "items": [
        {
          "idx": "1", 
          "xmin": "0", 
          "xmax": "2041.4217474125382", 
          "text": ""
        }, 
        {
          "idx": "2", 
          "xmin": "2041.4217474125382", 
          "xmax": "2041.968276643991", 
          "text": "this"
        }, 
        {
          "idx": "3", 
          "xmin": "2041.968276643991", 
          "xmax": "2042.5281632653062", 
          "text": "is"
        }, 
        {
          "idx": "4", 
          "xmin": "2042.5281632653062", 
          "xmax": "2044.0487352585324", 
          "text": "a"
        }, 
        {
          "idx": "5", 
          "xmin": "2044.0487352585324", 
          "xmax": "2045.144149659864", 
          "text": "demo"
        }
      ]
    }, 
    {
      "idx": "2", 
      "class": "IntervalTier", 
      "name": "phones", 
      "xmin": "0", 
      "xmax": "2045.144149659864", 
      "size": "12", 
      "items": [
        {
          "idx": "1", 
          "xmin": "0", 
          "xmax": "2041.4217474125382", 
          "text": "刚才我们看到短片当中介绍的年轻人啊"
        }, 
        {
          "idx": "2", 
          "xmin": "2041.4217474125382", 
          "xmax": "2041.5438290324326", 
          "text": "就是我们今天的嘉宾"
        }, 
        {
          "idx": "3", 
          "xmin": "2041.5438290324326", 
          "xmax": "2041.7321032910372", 
          "text": "嗯很多人已经介绍过他了"
        }, 
        {
          "idx": "4", 
          "xmin": "2041.7321032910372", 
          "xmax": "2041.968276643991", 
          "text": "什么天才呀"
        }, 
        {
          "idx": "5", 
          "xmin": "2041.968276643991", 
          "xmax": "2042.232189031843", 
          "text": "曾经是神童之类这样的词语"
        }, 
        {
          "idx": "6", 
          "xmin": "2042.232189031843", 
          "xmax": "2042.5281632653062", 
          "text": "嗯他的确是一个非常有才华的青年演奏家"
        }, 
        {
          "idx": "7", 
          "xmin": "2042.5281632653062", 
          "xmax": "2044.0487352585324", 
          "text": "如今已经是个青年人了"
        }, 
        {
          "idx": "8", 
          "xmin": "2044.0487352585324", 
          "xmax": "2044.2487352585324", 
          "text": "曾经是个很可爱的小神童"
        }, 
        {
          "idx": "9", 
          "xmin": "2044.2487352585324", 
          "xmax": "2044.3102321849011", 
          "text": "这样我们掌声有请李传韵"
        }, 
        {
          "idx": "10", 
          "xmin": "2044.3102321849011", 
          "xmax": "2044.5748932104329", 
          "text": "主持人，主持人好"
        }, 
        {
          "idx": "11", 
          "xmin": "2044.5748932104329", 
          "xmax": "2044.8329108578437", 
          "text": "我必须要先说一些，李传韵特别特别紧张。"
        }, 
        {
          "idx": "12", 
          "xmin": "2044.8329108578437", 
          "xmax": "2045.144149659864", 
          "text": "嗯"
        }
      ]
    }
  ]
}
```