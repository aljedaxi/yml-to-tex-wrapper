import argparse
import collections
from typing import Iterable
from subprocess import call
import pytest
from ruamel.yaml import YAML
from yml_to_tex import yml_to_tex as yml
yaml = YAML(typ='safe')

CONF = {
    'default_author': 'daxi'
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

def gen_parser():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('infile', help='the file you want to use.')
    parser.add_argument('-o', '--outfile', help='the file you want to use.')
    return parser.parse_args()

def impure_main():
    args = gen_parser()
    conf = CONF #TODO
    packages = ('ulem',) #TODO
    infile = args.infile
    outfile = get_outfile(args.outfile, infile)

    title = gen_title(filename)
    author = get_author(conf)

    infile_content = open(args.infile).read()
    outfile_content = make_latex(infile_content, title, author, packages)
    open(outfile, 'w').write(outfile_content)

    code_to_call = compile_pdf(outfile)
    for code in code_to_call:
        call(code)

if __name__ == '__main__':
    impure_main()

def test_compile_pdf():
    pytest.assume(compile_pdf('learning-to-program.tex'), [
        ('mkdir', 'junk_drawer'),
        ('latexmk', '--pdf', '-output-directory=junk_drawer', 'learning-to-program.tex'),
        ('mv', 'junk_drawer/learning-to-program.pdf', './')
    ])

    pytest.assume(compile_pdf('learning-to-program.tex', engine='pdflatex'), [
        ('mkdir', 'junk_drawer'),
        ('pdflatex', '-output-directory=junk_drawer', 'learning-to-program.tex'),
        ('mv', 'junk_drawer/learning-to-program.pdf', './')
    ])

def test_no_directories():
    pytest.assume(no_directories('test/test.tex'), 'test.tex')
    pytest.assume(no_directories('test.tex'), 'test.tex')

def test_no_extensions():
    pytest.assume(no_extensions('test/test.tex'), 'test/test')
    pytest.assume(no_extensions('test/test'), 'test/test')

def test_get_author():
    assert get_author({
        'default_author': 'daxi'
    }) == 'daxi'

def test_get_outfile():
    test_in = 'test_infile.yml'
    test_out = 'test_outfile.yml'
    pytest.assume(get_outfile(None, test_in), f"{test_in.split('.')[0]}.tex")
    pytest.assume(get_outfile(test_out, test_in), f"{test_out.split('.')[0]}.tex")
    pytest.assume(get_outfile(f'test/{test_out}', test_in), f"{test_out.split('.')[0]}.tex")

def test_gen_title():
    pytest.assume(gen_title('test_file.yml'), 'Test File')
    pytest.assume(gen_title('test-file.yml'), 'Test File')
    pytest.assume(gen_title('test/test-file.yml'), 'Test File')

def test_yml_to_tex():
    in_doc = open('test/learning-to-program.yml').read()
    out_doc = open('test/learning-to-program.tex').read()
    pytest.assume(yml_to_tex(in_doc), out_doc)

def test_make_latex():
    test_file_name = 'test/learning-to-program.yml'
    infile_content = open(test_file_name).read()
    outfile_content = open('test/full-learning-to-program.tex').read().rstrip()
    output = make_latex(infile_content, 'Learning To Program', ('ulem',), 'daxi')
    pytest.assume(output, outfile_content)
