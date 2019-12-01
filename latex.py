import argparse
import collections
from typing import Iterable
from subprocess import call
import pytest
from ruamel.yaml import YAML
from yml_to_tex import yml_to_tex as yml
yaml = YAML(typ='safe')

CONF = { #TODO
    'default_author': 'daxi',
    'packages': ('ulem',) 
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

def yml_to_tex(document: str) -> str:
    return yml.yml_to_tex(document)

def latex_boilerplate(title: str, author: str, body: str, packages: Iterable[str]) -> str:
    def format_packages(packages: Iterable[str]):
        return [f'\\usepackage{{{p}}}' for p in packages]

    body = ('\n').join(
        [f'\t{line}' for line in body.split('\n')]
    )
    prelude = '\\documentclass{article}'
    intro   = '\t\\maketitle\n\t\\tableofcontents'
    return ('\n').join((
        prelude,
        *format_packages(packages),
        f'\\title{{{title}}}',
        f'\\author{{{author}}}',
        f'\\begin{{document}}',
        intro,
        body,
        f'\\end{{document}}'
    ))

def make_latex(file_content: str, title: str, author: str, packages: Iterable[str]) -> str:
    body  = yml_to_tex(file_content)
    latex = latex_boilerplate(title, author, body, packages)
    return latex

def main(args, infile_content: str, conf: dict) -> dict:
    packages = conf['packages']
    infile = args.infile
    outfile = get_outfile(args.outfile, infile)

    title = gen_title(infile)
    author = get_author(conf)

    return {
        'outfile': outfile,
        'outfile_content': make_latex(infile_content, title, author, packages),
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
