# HomeWork_2

## About Me
**ID:** 65114540442
**Name:** ฟ้าใส ยุตะวัน

## Installation

git clone https://github.com/0xOat/HomeWork_2.git

```bash
  cd HomeWork_2
```
```bash
  pip install -r requirements.txt
```
```bash
  python manage.py runserver
```

## Data preparation
ข้อมูล embeddings และ metadata จะถูกเก็บแยกไฟล์กัน ต้องทำการดาวน์โหลด รวมไฟล์ แปลงเป็น CSV และนำเข้าสู่ ClickHouse

### ขั้นตอนที่ 1: สร้างไฟล์ download.sh และใส่โค้ดด้านล่าง

```bash
#!/bin/bash

number=${1}
if [[ $number == '' ]]; then
    number=1
fi

wget --tries=100 https://deploy.laion.ai/8f83b608504d46bb81708ec86e912220/embeddings/img_emb/img_emb_${number}.npy

wget --tries=100 https://deploy.laion.ai/8f83b608504d46bb81708ec86e912220/embeddings/text_emb/text_emb_${number}.npy

wget --tries=100 https://deploy.laion.ai/8f83b608504d46bb81708ec86e912220/embeddings/metadata/metadata_${number}.parquet

python3 process.py $number
```

### ขั้นตอนที่ 2: สร้างไฟล์ process.py
```python
import pandas as pd
import numpy as np
import os
import sys

str_i = str(sys.argv[1])
npy_file = "img_emb_" + str_i + '.npy'
metadata_file = "metadata_" + str_i + '.parquet'
text_npy = "text_emb_" + str_i + '.npy'

im_emb = np.load(npy_file)
text_emb = np.load(text_npy)
data = pd.read_parquet(metadata_file)

data = pd.concat([
    data, 
    pd.DataFrame({"image_embedding": [*im_emb]}), 
    pd.DataFrame({"text_embedding": [*text_emb]})
], axis=1, copy=False)

data = data[['url', 'caption', 'NSFW', 'similarity', "image_embedding", "text_embedding"]]

data['image_embedding'] = data['image_embedding'].apply(lambda x: list(x))
data['text_embedding'] = data['text_embedding'].apply(lambda x: list(x))

data['caption'] = data['caption'].apply(lambda x: x.replace("'", " ").replace('"', " "))

csv_filename = str_i + '.csv'
data.to_csv(csv_filename, header=False)

os.system(f"rm {npy_file} {metadata_file} {text_npy}")
```

### ขั้นตอนที่ 3: ให้สิทธิ์ในการรันไฟล์ download.sh
```bash
chmod +x download.sh
```

### ขั้นตอนที่ 4: ดาวน์โหลดและประมวลผลข้อมูล
```bash
./download.sh 1
```

## Setup ClickHouse
### ขั้นตอนที่ 1: เชื่อมต่อ ClickHouse
```bash
clickhouse-client
```

### ขั้นตอนที่ 2: สร้างตาราง
```sql
CREATE TABLE laion
(
    `id` Int64,
    `url` String,
    `caption` String,
    `NSFW` String,
    `similarity` Float32,
    `image_embedding` String,  
    `text_embedding` String    
)
ENGINE = MergeTree
ORDER BY id
SETTINGS index_granularity = 8192
```

### ขั้นตอนที่ 3: นำเข้าข้อมูล CSV
```sql
INSERT INTO laion FROM INFILE '/path/to/your/csv/files/*.csv'
```
หมายเหตุ: เปลี่ยน /path/to/your/csv/files/ เป็นเส้นทางจริงที่เก็บไฟล์ CSV