# الاستخدام:  python csv_to_json.py physics.csv     ->  ينتج data.json
# 1) ينقل أي صور jpg موجودة مباشرة في assets إلى مجلدات assets/img1 و img2 ... (900 ملف كحد أقصى لكل مجلد)
# 2) يحوّل physics.csv إلى data.json مع خريطة تحدد مجلد كل صورة
# ملاحظة: أرقام الدروس في الفيزياء متسلسلة عبر الوحدات (1..10) كما في ملف CSV
import csv, json, os, shutil, sys
MAX, A = 900, 'assets'
src = sys.argv[1] if len(sys.argv) > 1 else 'physics.csv'
num = lambda d: int(d[3:])
subs = lambda: sorted((d for d in os.listdir(A) if d.startswith('img') and d[3:].isdigit() and os.path.isdir(f'{A}/{d}')), key=num)

def organize():
    cnt = {d: len(os.listdir(f'{A}/{d}')) for d in subs()}
    for f in sorted(x for x in os.listdir(A) if x.lower().endswith('.jpg') and os.path.isfile(f'{A}/{x}')):
        d = next((d for d in cnt if cnt[d] < MAX), None)
        if d is None:
            d = f'img{len(cnt) + 1}'; os.makedirs(f'{A}/{d}'); cnt[d] = 0
        shutil.move(f'{A}/{f}', f'{A}/{d}/{f}'); cnt[d] += 1
    return cnt

cnt = organize()
found = {f[:-4]: num(d) for d in subs() for f in os.listdir(f'{A}/{d}') if f.endswith('.jpg')}
low = {k.lower(): k for k in found}
img = lambda n: n.strip() if n.strip() in found else low.get(n.strip().lower(), n.strip())

rows = list(csv.reader(open(src, encoding='utf-8-sig'), delimiter=';'))[1:]
Q = [{"c": int(r[1]), "l": int(r[2]), "t": int(r[3]), "q": img(r[5]), "s": img(r[6]),
      "o": [img(x) for x in r[7:11]], "y": r[11].strip()} for r in rows if r and r[0].strip()]
# الوحدات والدروس (الدرس برقمه العام كما في التطبيق الأصلي)
U = ["الميكانيكا","الكهرباء المتحركة","الكهرومغناطيسية"]
L = [[[1,"الزخم (كمية التحرك) الخطي والدفع"],[2,"التصادمات"],[3,"الحركة الدورانية"]],
     [[4,"التيار الكهربائي والمقاومة"],[5,"دارات التيار المستمر"]],
     [[6,"المجال المغناطيسي"],[7,"القوة المغناطيسية"],[8,"الحث الكهرومغناطيسي"]]]
# إخفاء الوحدات التي لا تحتوي أسئلة في الملف
have = {r["c"] for r in Q}
keep = [i for i in range(len(U)) if i + 1 in have]
data_units = [{"n": i + 1, "name": U[i], "lessons": [x for x in L[i] if any(r["c"] == i + 1 and r["l"] == x[0] for r in Q)]} for i in keep]
used = {n for r in Q for n in [r["q"], r["s"], *r["o"]]}
M = {n: found[n] for n in sorted(used) if n in found}
json.dump({"questions": Q, "units": data_units, "map": M}, open('data.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(len(Q), 'سؤال | ملفات كل مجلد:', cnt, '| صور مفقودة:', sorted(used - set(M)))
