"""
/*--------------------------------*- C++ -*----------------------------------*\
-------------------------------------------------------------------------------
 *****   ******   *          ***     *****   *     *  
*     *  *     *  *         *   *   *     *  *     *  
*        *     *  *        *     *  *        *     *  
 *****   ******   *        *******   *****   *******  
      *  *        *        *     *        *  *     *  
*     *  *        *        *     *  *     *  *     *  
 *****   *        *******  *     *   *****   *     *  
-------------------------------------------------------------------------------
 * SplashCaseCreator is part of Splash CFD automation tool.
 * Copyright (c) 2024 THAW TAR
 * Copyright (c) 2025 Mohamed Aly Sayed and Thaw Tar
 * All rights reserved.
 *
 * This software is licensed under the GNU Lesser General Public License version 3 (LGPL-3.0).
 * You may obtain a copy of the license at https://www.gnu.org/licenses/lgpl-3.0.en.html
 */
"""
##import os
##import inspect
##import pydoc
##from pathlib import Path
##from sphinx.application import Sphinx
##from weasyprint import HTML
##import importlib.util


##class DocumentationGenerator:
##    """
##    Generates documentation for the project, including HTML and PDF outputs.
##    """

##    @staticmethod
##    def generate_pydoc_html(source_file, output_dir="docs"):
##        """
##        Generates a raw HTML manual using `pydoc` for the specified source file.
##        :param source_file: Path to the Python file for which to generate documentation.
##        :param output_dir: Directory where the HTML file will be saved.
##        """
##        module_name = Path(source_file).stem
##        output_path = Path(output_dir) / f"{module_name}.html"
##        os.makedirs(output_dir, exist_ok=True)

##        # Dynamically import the module from the file path
##        try:
##            spec = importlib.util.spec_from_file_location(module_name, source_file)
##            module = importlib.util.module_from_spec(spec)
##            spec.loader.exec_module(module)
##        except Exception as e:
##            print(f"Error loading module: {e}")
##            return

##        # Generate HTML documentation
##        with open(output_path, "w") as f:
##            f.write(pydoc.HTMLDoc().docmodule(module))

##        print(f"HTML documentation generated at: {output_path}")

##    @staticmethod
##    def generate_sphinx_docs(source_dir, build_dir="docs/_build", format="html"):
##        """
##        Generates styled documentation using Sphinx.
##        :param source_dir: Directory where Sphinx source files are located.
##        :param build_dir: Directory where the Sphinx output will be built.
##        :param format: Output format (e.g., "html" or "pdf").
##        """
##        os.makedirs(build_dir, exist_ok=True)

##        # Initialize Sphinx app and build docs
##        app = Sphinx(
##            srcdir=source_dir,
##            confdir=source_dir,
##            outdir=build_dir,
##            doctreedir=os.path.join(build_dir, "doctrees"),
##            buildername=format,
##        )
##        app.build()

##        print(f"Sphinx documentation generated in {format} format at: {build_dir}")

##    @staticmethod
##    def convert_html_to_pdf(html_path, pdf_path):
##        """
##        Converts an HTML file to a PDF using WeasyPrint.
##        :param html_path: Path to the HTML file.
##        :param pdf_path: Path to save the output PDF file.
##        """
##        HTML(html_path).write_pdf(pdf_path)
##        print(f"PDF generated at: {pdf_path}")

##    @staticmethod
##    def generate_manual(source_file, output_dir="docs"):
##        """
##        Combines all the functionalities to generate an HTML and PDF manual.
##        :param source_file: Path to the main Python file for documentation.
##        :param output_dir: Directory to save the documentation.
##        """
##        module_name = Path(source_file).stem
##        html_output = Path(output_dir) / f"{module_name}.html"
##        pdf_output = Path(output_dir) / f"{module_name}.pdf"
##        os.makedirs(output_dir, exist_ok=True)

##        # Generate HTML using `pydoc`
##        DocumentationGenerator.generate_pydoc_html(source_file, output_dir)

##        # Check if HTML was successfully generated
##        if not html_output.exists():
##            print(f"Error: HTML file {html_output} not found.")
##            return

##        # Convert HTML to PDF
##        DocumentationGenerator.convert_html_to_pdf(html_output, pdf_output)

##        print(f"Documentation completed! HTML at {html_output}, PDF at {pdf_output}")



#import os
#import inspect
#import pydoc
#from pathlib import Path
#from sphinx.application import Sphinx
#from weasyprint import HTML
#import importlib.util
#from graphviz import Digraph  # For tree visualization
#from pylatex import Document, Section, Subsection, Command, NoEscape  # For LaTeX
#from pylatex.utils import escape_latex

#class DocumentationGenerator:
#    """
#    Generates professional documentation for the project, including a tree structure and detailed function/class documentation.
#    """

#    @staticmethod
#    def generate_tree_chart(source_file, output_dir="docs"):
#        """
#        Generates a tree chart of the code structure.
#        :param source_file: Path to the Python file.
#        :param output_dir: Directory where the tree chart will be saved.
#        :return: Path to the generated tree chart image.
#        """
#        output_path = Path(output_dir) / "code_structure_tree"
#        os.makedirs(output_dir, exist_ok=True)

#        # Dynamically import the module from the file path
#        try:
#            # Dynamically load the module from the given source file
#            spec = importlib.util.spec_from_file_location("module", source_file)
#            module = importlib.util.module_from_spec(spec)
#            spec.loader.exec_module(module)
#        except Exception as e:
#            print(f"Error loading module: {e}")
#            return None

#        # Initialize the tree visualization
#        tree = Digraph(
#            comment="Code Structure",
#            graph_attr={"size": "8,8", "rankdir": "LR", "fontsize": "12", "label": "Code Structure"}
#        )

#        # Analyze the structure of the module
#        for name, obj in inspect.getmembers(module):
#            if inspect.isclass(obj):
#                tree.node(name, label=f"Class: {name}", shape="box", style="filled", color="lightblue")
#                for method_name, method in inspect.getmembers(obj, predicate=inspect.isfunction):
#                    tree.node(method_name, label=f"Method: {method_name}", shape="ellipse", style="filled", color="lightgreen")
#                    tree.edge(name, method_name)
#            elif inspect.isfunction(obj):
#                tree.node(name, label=f"Function: {name}", shape="ellipse", style="filled", color="orange")

#        # Save the tree chart as a PNG image
#        tree_path = output_path.with_suffix(".png")
#        tree.render(tree_path.stem, format="png", directory=output_dir, cleanup=True)
#        print(f"Tree chart generated at: {tree_path}")
#        return tree_path

#    @staticmethod
#    def generate_latex_documentation(source_file, output_dir="docs"):
#        """
#        Generates a LaTeX-based PDF documentation with a tree chart and detailed documentation.
#        :param source_file: Path to the Python file for documentation.
#        :param output_dir: Directory where the LaTeX and PDF files will be saved.
#        """
#        module_name = Path(source_file).stem
#        os.makedirs(output_dir, exist_ok=True)
#        latex_file = Path(output_dir) / f"{module_name}.tex"
#        pdf_output = Path(output_dir) / f"{module_name}.pdf"

#        # Initialize LaTeX document
#        doc = Document()
#        doc.preamble.append(Command("title", module_name))
#        doc.preamble.append(Command("author", "Generated by DocumentationGenerator"))
#        doc.preamble.append(Command("date", NoEscape(r"\today")))
#        doc.append(NoEscape(r"\maketitle"))
#        doc.append(NoEscape(r"\tableofcontents"))

#        # Chapter 1: Code Structure with Tree Chart
#        doc.append(NoEscape(r"\chapter{Code Structure}"))
#        tree_chart_path = DocumentationGenerator.generate_tree_chart(source_file, output_dir)
#        if tree_chart_path:
#            doc.append(NoEscape(rf"\includegraphics[width=\textwidth]{{{tree_chart_path.stem}}}"))

#        # Chapter 2: Detailed Documentation
#        doc.append(NoEscape(r"\chapter{Function and Class Documentation}"))
#        try:
#            # Dynamically load the module
#            spec = importlib.util.spec_from_file_location(module_name, source_file)
#            module = importlib.util.module_from_spec(spec)
#            spec.loader.exec_module(module)
#        except Exception as e:
#            print(f"Error loading module: {e}")
#            return

#        # Document each class and function
#        for name, obj in inspect.getmembers(module):
#            if inspect.isclass(obj):
#                with doc.create(Section(f"Class: {name}")):
#                    doc.append(escape_latex(inspect.getdoc(obj) or "No documentation available."))
#                    for method_name, method in inspect.getmembers(obj, predicate=inspect.isfunction):
#                        with doc.create(Subsection(f"Method: {method_name}")):
#                            doc.append(escape_latex(inspect.getdoc(method) or "No documentation available."))
#            elif inspect.isfunction(obj):
#                with doc.create(Section(f"Function: {name}")):
#                    doc.append(escape_latex(inspect.getdoc(obj) or "No documentation available."))

#        # Generate the LaTeX file and compile it into a PDF
#        doc.generate_tex(str(latex_file))
#        doc.generate_pdf(str(latex_file.with_suffix("")), clean_tex=True)
#        print(f"LaTeX documentation generated at: {pdf_output}")

#    @staticmethod
#    def generate_manual(source_file, output_dir="docs"):
#        """
#        Combines tree chart and detailed documentation into a professional manual.
#        :param source_file: Path to the main Python file for documentation.
#        :param output_dir: Directory to save the manual.
#        """
#        try:
#            DocumentationGenerator.generate_tree_chart(source_file, output_dir)
#        except Exception as e:
#            print(f"Warning: Failed to generate tree chart. Error: {e}")
#        
#        try:
#            DocumentationGenerator.generate_latex_documentation(source_file, output_dir)
#        except Exception as e:
#            print(f"Error generating LaTeX documentation: {e}")
#        
#        print(f"Professional manual generated at: {output_dir}")

#        # Generate HTML using `pydoc`
#        DocumentationGenerator.generate_pydoc_html(source_file, output_dir)

#        # Check if HTML was successfully generated
#        if not html_output.exists():
#            print(f"Error: HTML file {html_output} not found.")
#            return

#        # Convert HTML to PDF
#        DocumentationGenerator.convert_html_to_pdf(html_output, pdf_output)

#        print(f"Documentation completed! HTML at {html_output}, PDF at {pdf_output}")

import os
import inspect
from pathlib import Path
import importlib.util
from graphviz import Digraph
from pylatex import Document, Section, Subsection, Command, NoEscape, Package
from pylatex.utils import escape_latex


class DocumentationGenerator:
    """
    Generates professional documentation for the project, including a tree structure and detailed function/class documentation.
    """

    @staticmethod
    def generate_tree_chart(source_file, output_dir="docs"):
        """
        Generates a tree chart of the code structure.
        :param source_file: Path to the Python file.
        :param output_dir: Directory where the tree chart will be saved.
        :return: Path to the generated tree chart image.
        """
        output_path = Path(output_dir) / "code_structure_tree"
        os.makedirs(output_dir, exist_ok=True)

        try:
            # Dynamically load the module from the given source file
            spec = importlib.util.spec_from_file_location("module", source_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as e:
            print(f"Error loading module: {e}")
            return None

        # Initialize the tree visualization
        tree = Digraph(
            comment="Code Structure",
            graph_attr={"size": "8,8", "rankdir": "LR", "fontsize": "12", "label": "Code Structure"}
        )

        # Analyze the structure of the module
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj):
                tree.node(name, label=f"Class: {name}", shape="box", style="filled", color="lightblue")
                for method_name, method in inspect.getmembers(obj, predicate=inspect.isfunction):
                    tree.node(method_name, label=f"Method: {method_name}", shape="ellipse", style="filled", color="lightgreen")
                    tree.edge(name, method_name)
            elif inspect.isfunction(obj):
                tree.node(name, label=f"Function: {name}", shape="ellipse", style="filled", color="orange")

        # Save the tree chart as a PNG image
        tree_path = output_path.with_suffix(".png")
        tree.render(tree_path.stem, format="png", directory=output_dir, cleanup=True)
        print(f"Tree chart generated at: {tree_path}")
        return tree_path

    @staticmethod
    def generate_latex_documentation(source_file, output_dir="docs"):
        """
        Generates a LaTeX-based PDF documentation with a tree chart and detailed documentation.
        :param source_file: Path to the Python file for documentation.
        :param output_dir: Directory where the LaTeX and PDF files will be saved.
        """
        module_name = "Splash Case Creator"
        os.makedirs(output_dir, exist_ok=True)
        latex_file = Path(output_dir) / "splash_case_creator"
        pdf_output = latex_file.with_suffix(".pdf")

        # Initialize LaTeX document
        doc = Document()
        doc.preamble.append(Command("title", module_name))
        doc.preamble.append(Command("author", "Generated by DocumentationGenerator"))
        doc.preamble.append(Command("date", NoEscape(r"\today")))
        doc.append(NoEscape(r"\maketitle"))
        doc.append(NoEscape(r"\tableofcontents"))
        doc.packages.append(Package("graphicx"))  # For including images

        # Chapter 1: Code Structure with Tree Chart
        doc.append(NoEscape(r"\chapter{Code Structure}"))
        tree_chart_path = DocumentationGenerator.generate_tree_chart(source_file, output_dir)
        if tree_chart_path:
            doc.append(NoEscape(r"\includegraphics[width=\textwidth]{" + str(tree_chart_path.stem) + "}"))

        # Chapter 2: Detailed Documentation
        doc.append(NoEscape(r"\chapter{Function and Class Documentation}"))
        try:
            # Dynamically load the module
            spec = importlib.util.spec_from_file_location(module_name, source_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as e:
            print(f"Error loading module: {e}")
            return

        # Document each class and function
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj):
                with doc.create(Section(f"Class: {name}")):
                    doc.append(escape_latex(inspect.getdoc(obj) or "No documentation available."))
                    for method_name, method in inspect.getmembers(obj, predicate=inspect.isfunction):
                        with doc.create(Subsection(f"Method: {method_name}")):
                            doc.append(escape_latex(inspect.getdoc(method) or "No documentation available."))
            elif inspect.isfunction(obj):
                with doc.create(Section(f"Function: {name}")):
                    doc.append(escape_latex(inspect.getdoc(obj) or "No documentation available."))

        # Generate the LaTeX file and compile it into a PDF
        doc.generate_pdf(str(latex_file), clean_tex=True)
        print(f"LaTeX documentation generated at: {pdf_output}")

    @staticmethod
    def generate_manual(source_file, output_dir="docs"):
        """
        Combines tree chart and detailed documentation into a professional manual.
        :param source_file: Path to the main Python file for documentation.
        :param output_dir: Directory to save the manual.
        """
        os.makedirs(output_dir, exist_ok=True)

        try:
            DocumentationGenerator.generate_tree_chart(source_file, output_dir)
        except Exception as e:
            print(f"Warning: Failed to generate tree chart. Error: {e}")

        try:
            DocumentationGenerator.generate_latex_documentation(source_file, output_dir)
        except Exception as e:
            print(f"Error generating LaTeX documentation: {e}")

        print(f"Professional manual generated at: {output_dir}")

