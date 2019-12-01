## HOW TO USE
  - clone this repo
    ```bash
    git clone https://github.com/aljedaxi/yml-to-tex-wrapper
    cd yml-to-tex-wrapper/
    git submodule init; git submodule update
    ```
  - make a yaml file
  - invoke repo on yaml file
    ```bash
    python yml-to-tex-wrapper/ my-file.yml
    ```
  - get pdf using the magic of LaTeX

## WHAT SHOULD THE YAML LOOK LIKE
  - the title is automagically generated from the filename
  - the author is declared at the top of latex.py #TODO!
```yaml
section 1:
  - point one
  - point two
  - point three
section 2:
  subsection 1: |
    prose and a lot of it
  subsection 2: prose and a little of it
```
