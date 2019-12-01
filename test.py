import latex
import pytest

def test_main():
    class Args():
        def __init__(self, infile, outfile):
            self.infile = infile
            self.outfile = outfile
    import json

    infile = 'test/learning-to-program.yml'
    args = Args(infile, None)
    conf = { #TODO
        'default_author': 'daxi',
        'packages': ('ulem',) 
    }
    pytest.assume(
        latex.main(args, open(infile).read(), conf),
        json.loads(open('test/test_main.json').read())
    )

def test_compile_pdf():
    pytest.assume(latex.compile_pdf('learning-to-program.tex'), [
        ('mkdir', 'junk_drawer'),
        ('latexmk', '--pdf', '-output-directory=junk_drawer', 'learning-to-program.tex'),
        ('mv', 'junk_drawer/learning-to-program.pdf', './')
    ])

    pytest.assume(latex.compile_pdf('learning-to-program.tex', engine='pdflatex'), [
        ('mkdir', 'junk_drawer'),
        ('pdflatex', '-output-directory=junk_drawer', 'learning-to-program.tex'),
        ('mv', 'junk_drawer/learning-to-program.pdf', './')
    ])

def test_no_directories():
    pytest.assume(latex.no_directories('test/test.tex'), 'test.tex')
    pytest.assume(latex.no_directories('test.tex'), 'test.tex')

def test_no_extensions():
    pytest.assume(latex.no_extensions('test/test.tex'), 'test/test')
    pytest.assume(latex.no_extensions('test/test'), 'test/test')

def test_get_author():
    assert latex.get_author({
        'default_author': 'daxi'
    }) == 'daxi'

def test_get_outfile():
    test_in = 'test_infile.yml'
    test_out = 'test_outfile.yml'
    pytest.assume(latex.get_outfile(None, test_in), f"{test_in.split('.')[0]}.tex")
    pytest.assume(latex.get_outfile(test_out, test_in), f"{test_out.split('.')[0]}.tex")
    pytest.assume(latex.get_outfile(f'test/{test_out}', test_in), f"{test_out.split('.')[0]}.tex")

def test_gen_title():
    pytest.assume(latex.gen_title('test_file.yml'), 'Test File')
    pytest.assume(latex.gen_title('test-file.yml'), 'Test File')
    pytest.assume(latex.gen_title('test/test-file.yml'), 'Test File')

def test_yml_to_tex():
    in_doc = open('test/learning-to-program.yml').read()
    out_doc = open('test/learning-to-program.tex').read()
    pytest.assume(latex.yml_to_tex(in_doc), out_doc)

def test_make_latex():
    test_file_name = 'test/learning-to-program.yml'
    infile_content = open(test_file_name).read()
    outfile_content = open('test/full-learning-to-program.tex').read().rstrip()
    output = latex.make_latex(infile_content, 'Learning To Program', ('ulem',), 'daxi')
    pytest.assume(output, outfile_content)
