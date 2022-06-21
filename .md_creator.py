import json
from typing import Iterable
class Assembler:
    def __init__(self,rawlist:list,data:dict,pre:str)->None:
        self.text=pre
        self.data=data
        self.raw=rawlist
        self.tags=self.data.get('tags',{})
        self.plugs=self.data.get('plugins',{})
        self.ind1='  '*1+'*'
        self.ind2='  '*2+'*'
    def create(self)->str:
        self.init_tags()
        self.init_plugs()
        self.create_docs()
        self.create_raw()
        self.create_tags()
        return self.text
    def init_tags(self)->None:
        self.linktags=set(self.tags)
    def init_plugs(self)->None:
        self.linkplugs=set(self.data.get('forcelink',[]))
        for maincategory in self.plugs.values():
            for subcategory in maincategory.values():
                for plugdata in subcategory.values():
                    self.linkplugs|=set(i for i in plugdata.get('requiers',[]))
                    self.linkplugs|=set(i for i in plugdata.get('optional',[]))
    def create_docs(self)->None:
        self.text+='# Documented-list\n'
        for name,maincategory in self.plugs.items():
            self.text+=f'## {name}\n'
            for name,subcategory in maincategory.items():
                self.text+=f'### {name}\n'
                for name,plugdata in subcategory.items():
                    self.raw.remove(name)
                    self.doc_from_plug(name,plugdata)
    def doc_from_plug(self,name:str,plugdata:dict)->None:
        doc=''
        if name in self.linkplugs:
            doc+=f'{self.ind1} ###### [{name}](https://github.com/{name})\n'
        else:
            doc+=f'{self.ind1} [{name}](https://github.com/{name})\n'
        if (tags:=plugdata.get('tags',[])):
            doc+=f'{self.ind2} Tags: '+', '.join(self.tolink(i) if i in self.linktags else i for i in tags)+'\n'
        doc+=self.list2str(f'{self.ind2} Requiers',[self.plugtolink(i) for i in plugdata.get('requiers',[])])
        doc+=self.list2str(f'{self.ind2} Requirements',plugdata.get('requirements',[]))
        doc+=self.list2str(f'{self.ind2} Optional/extensions',[self.plugtolink(i) for i in plugdata.get('optional',[])])
        if (docs:=plugdata.get('docs','')):
            doc+=f'{self.ind2} '+docs+'\n'
        self.text+=doc
    @staticmethod
    def tolink(x:str)->str:
        return f'[{x}](#{x})'
    @staticmethod
    def plugtolink(x:str)->str:
        return f'[{x}](#{x.replace("/","").replace(".","")})'
    @staticmethod
    def list2str(title:str,x:list)->str:
        if len(x):return title+': '+', '.join(x)+'\n'
        else:return ''
    def create_raw(self)->None:
        self.text+='# Non-documented-list\n'
        self.text+='\n'.join(f'* ###### [{i}](https://github.com/{i})' if i in self.linkplugs else f'* [{i}](https://github.com/{i})' for i in self.raw)+'\n'
    def create_tags(self)->None:
        self.text+='# Tags\n'
        self.text+='\n'.join(f'* ###### {name}\n{tagdata}' for name,tagdata in self.tags.items())
def main():
    with open('raw') as f:
        rawlist=f.read().split('\n')
    with open('data.json') as f:
        data=json.load(f)
    pre=r'''# vim-plugin-list
This is a list of plugins.
_TODO: categorize, document and remove not plugins_

_NOTE: this list may contain: mirrors, extensions to plugins, links that are not working and other things that are not related to vim plugins._

_Other vim plugin lists: [awesome-vim](https://github.com/akrawchyk/awesome-vim), [neovim-official-list](https://github.com/neovim/neovim/wiki/Related-projects#plugins)_

'''
    with open('README.md','w') as f:
        f.write(Assembler(rawlist,data,pre).create())
if __name__=="__main__":
    main()
