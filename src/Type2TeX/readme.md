# Type2TeX

Type2TeX is a script converts MathType .eps/none files into LaTeX equations.

The script is based on [the solution](https://dev.to/furkan_kalkan1/quick-hack-converting-mathml-to-latex-159c).

## Usage
```
py main.py [-p <project_root>] [-b <build_root>] [-f] <scan_root>
```

|argument|default value|description|
|:--|:--|:--|
|scan_root          | *NONE*    | a root directory were the script will look for .eps files to convert them into .tex code|
|-b, --build_root   |./build    | a root directory were the generated files will be placed. The directory will have the same structure as an original one. Another words .eps files will have the same 'proj_root'-relative paths as the .tex 'build-root'-relative ones |
|-p, --proj_root    |./         | a directory is being used to calculate equation categories |
|-f, --force        |false      | disables [a lazy generation](#lazy-generation)


### Lazy generation
By default the scripts doesn't repeat self twice and generates a new formula only ones and recompiles it only when an original .eps file is newer than the generated .tex one. It means if a .tex file's modification date is newer or equal than a .eps' one the file wont be reconverted.

It might be usefull to force the reconvertion due to some reason. In this case the lazy generation disables with use of a ```-f``` flag.
