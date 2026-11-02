#!/usr/bin/env python3
"""Build small attributed PDF extracts from explicitly licensed open coursebooks."""
import fitz, requests, re, json
from pathlib import Path
from tempfile import TemporaryDirectory

root=Path(__file__).resolve().parents[1]
out=root/'readings'
out.mkdir(exist_ok=True)
sources={
 'mit':('https://diffusion.csail.mit.edu/2026/docs/lecture_notes.pdf','Holderrieth','CC BY-NC-SA',4),
 'calc':(['https://d3bxy9euw4e147.cloudfront.net/oscms-prodcms/media/documents/CalculusVolume3-LR.pdf','https://raw.githubusercontent.com/librescholar/open-textbooks/main/Calculus3_openstax_2.pdf','https://assets.openstax.org/oscms-prodcms/media/documents/Calculus_Volume_3_-_WEB.pdf'],'OpenStax','CC BY-NC-SA 4.0',30),
 'stat':(['https://raw.githubusercontent.com/RachaelDavou/Multi-Agent-AI-Academic-Assistant/main/data/course_catalogue/Introductory%20Statistics%202e.pdf','https://assets.openstax.org/oscms-prodcms/media/documents/Introductory_Statistics_2e_-_WEB.pdf'],'OpenStax','CC BY 4.0',30),
}
# file, source, start heading, first following heading, maximum excerpt pages.
jobs=[
 ('week01/01_partial_derivatives.pdf','calc',('4.3','Partial Derivatives'),('4.4','Tangent Planes'),14),
 ('week01/02_chain_rule.pdf','calc',('4.5','The Chain Rule'),('4.6','Directional Derivatives'),15),
 ('week01/03_gradient.pdf','calc',('4.6','Directional Derivatives'),('4.7','Maxima'),20),
 ('week01/04_probability.pdf','stat',('3.1','Terminology'),('3.4','Contingency Tables'),27),
 ('week01/05_expectation.pdf','stat',('4.1','Probability Distribution Function'),('4.3','Binomial Distribution'),20),
 ('week01/06_gaussian.pdf','stat',('6.1','The Standard Normal Distribution'),('6.2','Using the Normal Distribution'),16),
 ('week01/07_conditional_expectation.pdf','mit',('A.2','Conditional densities and expectations'),None,4),
 ('week02/01_flow_diffusion.pdf','mit',('2','Flow and Diffusion Models'),('3','Flow Matching'),16),
 ('week03/01_flow_matching.pdf','mit',('3','Flow Matching'),('4','Score Functions'),17),
 ('week05/01_score_matching.pdf','mit',('4','Score Functions and Score Matching'),('5','Guidance'),17),
]
def section(doc,word,from_page):
    n,t=word
    pat=re.compile(r'(?<![0-9])'+re.escape(n)+r'\s*'+re.escape(t),re.I)
    for i in range(from_page,len(doc)):
        txt=re.sub(r'\s+',' ',doc[i].get_text(sort=True)[:1300])
        m=pat.search(txt[:650])
        if m and m.start()<400: return i
    raise ValueError('Cannot locate PDF section heading '+str(word))
def main():
    manifest=[];errors=[]
    with TemporaryDirectory() as tmp:
        docs={}
        for kind,(url,guard,license,min_page) in sources.items():
            try:
                attempts=[]
                for candidate in (url if isinstance(url,list) else [url]):
                    try:
                        r=requests.get(candidate,timeout=150,headers={'User-Agent':'Mozilla/5.0'})
                        r.raise_for_status()
                        if not r.content.startswith(b'%PDF-'):raise ValueError('Not a PDF')
                        url=candidate
                        break
                    except Exception as exc:
                        attempts.append(str(exc))
                else:raise ValueError('All source URLs failed: '+'; '.join(attempts))
                path=Path(tmp)/(kind+'.pdf');path.write_bytes(r.content)
                doc=fitz.open(path)
                if len(doc)<65: raise ValueError('Suspicious short PDF')
                sample=' '.join(doc[i].get_text()[:1200] for i in range(min(len(doc),25)))
                if guard.lower() not in sample.lower():raise ValueError('Unexpected source content/title')
                docs[kind]=(doc,url,license,min_page)
                print('Verified original',kind,len(doc),'pages')
            except Exception as e:errors.append(f'{kind} source: {e}')
        for name,kind,start,end,max_pages in jobs:
            if kind not in docs: continue
            doc,url,license,min_page=docs[kind]
            try:
                a=section(doc,start,min_page)
                bounded=False
                if end:
                    try:
                        b=section(doc,end,a+1)
                        if not (1<=b-a<=max_pages): raise ValueError('next section too distant')
                    except ValueError:
                        b=min(len(doc),a,min(a+8,a+max_pages))
                        bounded=True
                else:
                    b=min(len(doc),a+max_pages)
                if not (1<=b-a<=max_pages):raise ValueError(f'Implausible length {b-a} starting {a}')
                clip=fitz.open();clip.insert_pdf(doc,from_page=a,to_page=b-1)
                path=out/name;path.parent.mkdir(parents=True,exist_ok=True)
                clip.set_metadata({'title':start[0]+' '+start[1], 'subject':'Excerpt from '+url+'; licensed '+license+'.'})
                clip.save(path,garbage=4,deflate=True)
                clip.close()
                manifest.append({'path':str(path.relative_to(root)),'section':start[0]+' '+start[1],'source_pdf_pages':f'{a+1}-{b}','license':license,'original':url,'bytes':path.stat().st_size,'boundary_note':'First 8 PDF pages from verified section start (next section not found)' if bounded else 'Exact section boundary'})
                print('Extracted',name, b-a,'pages')
            except Exception as e:errors.append(f'{name}: {e}')
        for doc,_,_,_ in docs.values():doc.close()
    (out/'manifest.json').write_text(json.dumps({'files':manifest,'warnings':errors},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('EXCERPTS',len(manifest),'WARNINGS',errors)
    if not manifest:raise SystemExit('No matching licensed excerpts found')
if __name__=='__main__': main()
