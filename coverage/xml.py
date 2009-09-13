"""Cobertura reporting"""

import os
import sys
import xml.dom.minidom

from coverage.report import Reporter


class CoberturaReporter(Reporter):
    """A reporter for writing the summary report."""
    
    def __init__(self, coverage, ignore_errors=False):
        super(CoberturaReporter, self).__init__(coverage, ignore_errors)

    def report(self, morfs, omit_prefixes=None, outfile=None):
        """Generate a Cobertura report for `morfs`.
        
        `morfs` is a list of modules or filenames.  `directory` is where to put
        the Cobertura XML file. `omit_prefixes` is a list of strings, prefixes of
        modules to omit from the report.
        
        """
        #
        # Initial setup
        #
        if not outfile:
            outfile = sys.stdout
        self.find_code_units(morfs, omit_prefixes)
        #
        # Create the DOM that will store the data
        #
        impl = xml.dom.minidom.getDOMImplementation()
        docType = impl.createDocumentType(
            "coverage", None,
            "http://cobertura.sourceforge.net/xml/coverage-03.dtd" )
        doc = impl.createDocument(None, "coverage", docType)
        root = doc.documentElement

        packageXml = doc.createElement("packages")
        root.appendChild(packageXml)
        packages = {}

        errors = False
        for cu in self.code_units:
            #
            # Create the 'lines' and 'package' XML elements, which
            # are populated later.  Note that a package == a directory.
            #
            (dir, fname) = os.path.split(cu.name)
            print "HERE",dir,":",fname
            if dir is '':
                dir = '.'
            package = packages.setdefault(
                dir, [ doc.createElement("package"), {},
                    0, 0, 0, 0 ] )
            c = doc.createElement("class")
            lines = doc.createElement("lines")
            c.appendChild(lines)
            className = fname.replace('.', '_')
            c.setAttribute("name", className)
            c.setAttribute("filename", cu.name)
            c.setAttribute("complexity", "0.0")


            try:
                statements, _, missing, readable = self.coverage._analyze(cu)
                #
                # for each statement, create an XML 'line' element
                #
                for line in statements:
                    l = doc.createElement("line")
                    l.setAttribute("number", str(line))
                    #
                    # Q: can we get info about the number of times
                    # a statement is executed?  If so, that should be
                    # recorded here.
                    #
                    if not line in missing:
                        l.setAttribute("hits", str(1))
                    #
                    # Q: can we get info about whether this statement
                    # is a branch?  If so, that data should be
                    # used here.
                    #
                    l.setAttribute("branch", "false")
                    lines.appendChild(l)
                class_lines = 1.0*len(statements)
                class_hits = class_lines - len(missing)
                class_branches = 0.0
                class_branch_hits = 0.0

                #
                # Finalize the statistics that are collected
                # in the XML DOM.
                #
                c.setAttribute("line-rate", str(class_hits / (class_lines or 1.0)))
                c.setAttribute( "branch-rate", str(class_branch_hits / (class_branches or 1.0)) )
                package[1][className] = c
                package[2] += class_hits
                package[3] += class_lines
                package[4] += class_branch_hits
                package[5] += class_branches
            except KeyboardInterrupt:                       #pragma: no cover
                raise
            except:
                if not self.ignore_errors:
                    typ, msg = sys.exc_info()[:2]
                    fmt_err = "%s   %s: %s\n"
                    outfile.write(fmt_err % (cu.name, typ.__name__, msg))
                    errors=True
   
        #
        # Don't write the XML data if we've encountered errors
        #
        if errors:
            return

        #
        # Populate the XML DOM with the package info
        #
        for packageName, packageData in packages.items():
            package = packageData[0];
            packageXml.appendChild(package)
            classes = doc.createElement("classes")
            package.appendChild(classes)
            classNames = packageData[1].keys()
            classNames.sort()
            for className in classNames:
                classes.appendChild(packageData[1][className])
            package.setAttribute("name", packageName.replace(os.sep, '.'))
            package.setAttribute("line-rate", str(packageData[2]/(packageData[3] or 1.0)))
            package.setAttribute( "branch-rate", str(packageData[4] / (packageData[5] or 1.0) ))
            package.setAttribute("complexity", "0.0")

        #
        # Use the DOM to write the output file
        #
        outfile.write( doc.toprettyxml() )