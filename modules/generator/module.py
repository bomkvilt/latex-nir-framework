from mako.template import Template
from os import path
import argparse, os, glob


class Generator:
    def __init__(self,
        build_path:str, # path to a build directory root
        proj_path:str,  # path to a project root directory
        
        src_eqs_name:str     = "eqs",           # section-relative path to equations root
        src_fig_name:str     = "fig",           # section-relative path to figures   root
        gen_module_name:str  = "[autogen].tex", # name of module's  generated path
        gen_section_name:str = "[autogen].tex", # name of section's generated path
    ):
        self.module_root = path.dirname(path.realpath(__file__))
        self.generators  = {
            "section" : self._do_generation_section,
            "package" : self._do_generation_package,
        }

        self._build_path = self._fix_path_(build_path)
        self._proj_path  = self._fix_path_(proj_path)

        self._src_eqs_name     = src_eqs_name
        self._src_fig_name     = src_fig_name
        self._gen_module_name  = gen_module_name
        self._gen_section_name = gen_section_name

    def assignToArgParser(self, parser:argparse.ArgumentParser) -> any:
        parser.add_argument("type", choices=self.generators.keys(),
            help="type of a target entity (directory)")
        parser.add_argument("path",
            help="path to a target entity")
        return self._do_generation_

# private:

    # replaces :/ token to the module's root path
    def _fix_path_(self, path0:str) -> str:
        if path0.startswith(":/"):
            path0 = path.join(self.module_root, path0[2:])
        elif not path.isabs(path0):
            path0 = path.abspath(path0)
        return path0.replace("\\", "/")

    def _sanitize_path(self, path0:str) -> str:
        return path0.replace("\\", "/")

    def _do_generation_(self, args):
        callback = self.generators.get(args.type)
        if not callback:
            raise RuntimeError("unexpected generator type '{}'".format(args.type))        
        
        args.path = self._fix_path_(args.path)
        count = args.path.count(":all:")
        if (count == 1 and not args.path.endswith(":all:")) or count > 1:
            raise RuntimeError(":all: placeholder must only be placed in the end of the path '{}'".format(args.path))
        if count == 0: 
            callback(args.type, args.path)
            return
        for subpath in glob.iglob(args.path.replace(":all:", "*"), recursive=False):
            callback(args.type, subpath)
    
    def _do_generation_section(self, type:str, abs_target_path:str):
        # the section's sanisized root-relative path
        category = path.relpath(abs_target_path, self._proj_path).replace("..", "")
        # abs path to a destination autogenerating file
        tex_path = "/".join([abs_target_path, self._gen_section_name])
        # section-relative path to the section's build subdirectory
        build_path = "/".join([path.relpath(self._build_path, abs_target_path), category])
        # rendering of a section template
        self._render_template(tex_path, ":/templates/section.tmpl.tex", (
            {
                'var': "frm_root_equations",
                'val': self._src_eqs_name,
                'exp': "section-relative path to equations root directory",
            },
            {
                'var': "frm_root_figures",
                'val': self._src_fig_name,
                'exp': "section-relative path to figures root directory",
            },
            {
                'var': "frm_root_document",
                'val': self._sanitize_path(path.relpath(self._proj_path, abs_target_path)),
                'exp': "section-relative path to document root directory",
            },
            {
                'var': "frm_name_section",
                'val': path.basename(abs_target_path),
                'exp': "the section's name",
            },
            {
                'var': "frm_root_autogen",
                'val': self._sanitize_path(build_path),
                'exp': "the section's build directory",
            }
        ))

    def _do_generation_package(self, type:str, abs_target_path:str):
        pass

    def _render_template(self, tex_path:str, tmpl_path:str, args:dict):
        template = Template(filename=self._fix_path_(tmpl_path))
        tex_text = template.render(vars=args).replace("\n\n", "\n")
        with open(tex_path, 'w') as tex_file:
            tex_file.write(tex_text)
            tex_file.close()
