import ast
import re
from typing import Dict, List, Any

class CodeAnalyzer:
    """Analyze code changes for various metrics"""
    
    def analyze_diff(self, diff_text: str) -> Dict[str, Any]:
        """Analyze code diff for structural changes"""
        analysis = {
            "functions_added": [],
            "functions_modified": [],
            "functions_removed": [],
            "dependencies_changed": [],
            "complexity_metrics": {}
        }
        
        # Parse diff to identify changes
        files = self._parse_diff(diff_text)
        
        for file in files:
            # Analyze each file
            file_analysis = self._analyze_file(file)
            analysis["functions_added"].extend(file_analysis["functions_added"])
            analysis["functions_modified"].extend(file_analysis["functions_modified"])
            analysis["functions_removed"].extend(file_analysis["functions_removed"])
            analysis["dependencies_changed"].extend(file_analysis["dependencies_changed"])
            
        return analysis
        
    def _parse_diff(self, diff_text: str) -> List[Dict]:
        """Parse diff text into structured file changes"""
        files = []
        current_file = None
        
        for line in diff_text.split('\n'):
            if line.startswith('--- a/'):
                if current_file:
                    files.append(current_file)
                filename = line[6:]  # Remove '--- a/'
                current_file = {
                    "filename": filename,
                    "changes": []
                }
            elif current_file and (line.startswith('+') or line.startswith('-')):
                if not line.startswith('+++') and not line.startswith('---'):
                    current_file["changes"].append(line)
                    
        if current_file:
            files.append(current_file)
            
        return files
        
    def _analyze_file(self, file_data: Dict) -> Dict[str, List]:
        """Analyze a single file for changes"""
        result = {
            "functions_added": [],
            "functions_modified": [],
            "functions_removed": [],
            "dependencies_changed": []
        }
        
        # This is a simplified analyzer - in practice, you'd use AST parsing
        content = "\n".join([line[1:] for line in file_data["changes"] if line.startswith('+')])
        
        # Simple function detection
        function_matches = re.findall(r'def\s+(\w+)\s*\(', content)
        result["functions_added"] = function_matches
        
        return result
        
    def calculate_complexity(self, code: str) -> Dict[str, int]:
        """Calculate code complexity metrics"""
        try:
            tree = ast.parse(code)
            visitor = ComplexityVisitor()
            visitor.visit(tree)
            
            return {
                "cyclomatic_complexity": visitor.complexity,
                "function_count": visitor.function_count,
                "nesting_depth": visitor.max_nesting_depth
            }
        except:
            return {
                "cyclomatic_complexity": 0,
                "function_count": 0,
                "nesting_depth": 0
            }

class ComplexityVisitor(ast.NodeVisitor):
    """AST visitor to calculate complexity metrics"""
    
    def __init__(self):
        self.complexity = 1
        self.function_count = 0
        self.current_nesting = 0
        self.max_nesting_depth = 0
        
    def visit_FunctionDef(self, node):
        self.function_count += 1
        self.generic_visit(node)
        
    def visit_If(self, node):
        self.complexity += 1
        self._handle_nested_structure(node)
        
    def visit_For(self, node):
        self.complexity += 1
        self._handle_nested_structure(node)
        
    def visit_While(self, node):
        self.complexity += 1
        self._handle_nested_structure(node)
        
    def visit_Try(self, node):
        self.complexity += 1
        self._handle_nested_structure(node)
        
    def _handle_nested_structure(self, node):
        self.current_nesting += 1
        self.max_nesting_depth = max(self.max_nesting_depth, self.current_nesting)
        self.generic_visit(node)
        self.current_nesting -= 1