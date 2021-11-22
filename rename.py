import os

path = "D:\\Code\\projects\\3380scrape\\html\\"

files = os.listdir("html")

idx = 0
for file in files:
    try:
        os.rename(os.path.join(path, file), os.path.join(path, file[:-5]))
        idx += 1
        if idx % 100 == 0:
            print(idx)

    except:
        continue

