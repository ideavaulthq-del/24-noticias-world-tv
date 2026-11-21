import json, urllib.request, urllib.parse, xml.etree.ElementTree as ET, datetime, pathlib, re
topics={"world":"world","ukraine":"Ukraine Russia","portugal":"Portugal","economy":"world economy energy"}
out={"updated_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"categories":{}}
for key,query in topics.items():
    url="https://news.google.com/rss/search?"+urllib.parse.urlencode({"q":query,"hl":"pt-PT","gl":"PT","ceid":"PT:pt-150"})
    items=[]
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 GEOWATCH/1.0"})
        with urllib.request.urlopen(req,timeout=18) as response: root=ET.fromstring(response.read())
        for item in root.findall("./channel/item")[:15]:
            title=item.findtext("title","").strip()
            link=item.findtext("link","").strip()
            source=item.findtext("source","Google Notícias").strip()
            date=item.findtext("pubDate","")
            if title and link.startswith("https://"): items.append({"title":title,"link":link,"source":source,"date":date})
    except Exception as exc: print(key,repr(exc))
    out["categories"][key]=items
pathlib.Path("geowatch-360-news").mkdir(exist_ok=True)
pathlib.Path("geowatch-360-news/news.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
print({k:len(v) for k,v in out["categories"].items()})
