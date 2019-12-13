import argparse
import collections
from typing import Iterable
from subprocess import call
import re
import pytest
from ruamel.yaml import YAML
from yml_to_tex import yml_to_tex as yml
yaml = YAML(typ='safe')

CONF = { #TODO
    'default_author': 'daxi',
    'packages': (
        'ulem',
     ),
     'commands': (
        '\\renewcommand{\\labelenumii}{\\theenumii}',
        '\\renewcommand{\\theenumii}{\\theenumi.\\arabic{enumii}.}',
        '\\renewcommand{\\labelenumiii}{\\theenumiii}',
        '\\renewcommand{\\theenumiii}{\\theenumii\\arabic{enumiii}.}',
        '\\renewcommand{\\labelenumiv}{\\theenumiv}',
        '\\renewcommand{\\theenumiv}{\\theenumiii\arabic{enumiv}.}',
     ),
}
DESCRIPTION = 'takes a yaml file in, return a pdf---if you did it right.'

def no_extensions(filename: str) -> str:
    if '.' in filename:
        return filename.split('.')[0]
    else:
        return filename

def no_directories(filename: str) -> str:
    if '/' in filename:
        return filename.split('/')[-1]
    else:
        return filename

def compile_pdf(filename: str, engine=("latexmk", "--pdf"), out_dir="junk_drawer") -> tuple:
    engine = (*engine, f"-output-directory={out_dir}")
    extensionless = no_extensions(filename)

    code_to_call = (
        ("mkdir", out_dir),
        (*engine, filename),
        ("mv", f"{out_dir}/{extensionless}.pdf", "./")
    )

    return code_to_call

def get_outfile(outfile, infile: str) -> str:
    def either(left, right):
        if left:
            return left
        else:
            return right
    def tex(s: str) -> str:
        return f'{s}.tex'

    return tex(no_directories(no_extensions(either(outfile, infile))))

def get_author(conf: dict) -> str:
    return conf['default_author']

def gen_title(filename: str) -> str:
    #TODO camel case files? don't care.
    filename = no_directories(no_extensions(filename))

    return filename.replace('_', ' ').replace('-', ' ').title()

def yml_to_tex(infile: str, meta={}) -> str:
    def split_into_docs(doc: str) -> tuple:
        try:
            documents = re.compile('\n---').split(infile)
        except:
            documents = (infile, )

        return documents

    def rip_metadata_from_doc(doc_dicts: dict, meta: dict) -> tuple:
        for dic in doc_dicts:
            for key in dic:
                if key in meta.keys():
                    meta[key] = dic[key]
                    del dic[key]

        return (doc_dicts, meta)

    def chapter_together(chapters: list, chapter_titles=('', )) -> str:
        #TODO each chapter should have the form
        #(title, body)
        #[f'\\chapter{{{title}}}\n{body} for (title, body) in chapters]
        joiner = '\\chapter{unnamed}\n'
        return '\n'.join(
            [f'{joiner}{chapter}' for chapter in chapters]
        )

    doc_dicts = [yaml.load(document) for document in split_into_docs(infile)]
    (doc_dicts, meta) = rip_metadata_from_doc(doc_dicts, meta)
    if len(doc_dicts) == 1:
        return {
            'document': yml.data_to_tex(doc_dicts[0]),
            'documentclass': 'article',
            'meta': meta
        }
    else:
        return {
            'document': chapter_together(
                [yml.data_to_tex(doc) for doc in doc_dicts]
            ),
            'documentclass': 'book',
            'meta': meta
        }

def latex_boilerplate(meta: dict, body: str, packages=('',), commands=('',)) -> str:
    def format_packages(packages: Iterable[str]):
        return [f'\\usepackage{{{p}}}' for p in packages]

    author = meta['author']
    documentclass = meta['documentclass']
    title = meta['title']

    prelude = f'\\documentclass{{{documentclass}}}' \
        f'\\title{{{title}}}' \
        f'\\author{{{author}}}'

    intro   = '\t\\maketitle\n\t\\tableofcontents'

    body = ('\n').join(
        [f'\t{line}' for line in body.split('\n')]
    )

    return ('\n').join((
        prelude,
        *format_packages(packages),
        *commands,
        '\\begin{document}',
        intro,
        body,
        '\\end{document}'
    ))

def make_latex(file_content: str, title: str, author: str, packages=('',), commands=('',)) -> str:
    meta = {
        'title': title,
        'author': author,
    }
    temp = yml_to_tex(file_content, meta=meta)
    document = temp['document']
    meta = temp['meta']
    meta['documentclass'] = temp['documentclass']
    latex = latex_boilerplate(meta, document, packages, commands)
    return latex

def main(args, infile_content: str, conf: dict) -> dict:
    def safe_prop(dic: dict, prop: str, default=None):
        try:
            val = dic[prop]
        except:
            val = default

        return val

    packages = safe_prop(conf, 'packages', default=('',))
    commands = safe_prop(conf, 'commands', default=('',))

    infile = args.infile
    outfile = get_outfile(args.outfile, infile)

    title = gen_title(infile)
    author = get_author(conf)

    return {
        'outfile': outfile,
        'outfile_content': make_latex(
            infile_content.replace('_', '\\_'), 
            title, 
            author, 
            packages, 
            commands
        ),
        'sh_code': compile_pdf(outfile)
    }

def impure_main():
    args = gen_parser()
    infile_content = open(args.infile).read()
    IO = main(args, infile_content, CONF)
    open(IO['outfile'], 'w').write(IO['outfile_content'])

    for code in IO['sh_code']:
        call(code)

def gen_parser():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('infile', help='the file you want to use.')
    parser.add_argument('-o', '--outfile', help='the file you want to use.')
    return parser.parse_args()

if __name__ == '__main__':
    impure_main()
