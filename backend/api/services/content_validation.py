import subprocess
import tempfile
import os
import sys
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import re
from datetime import datetime
import ast
import json

class ValidationResult(Enum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"

@dataclass
class ValidationIssue:
    """Represents a single validation issue found in content."""
    id: str
    type: str  # 'technical_accuracy', 'reproducibility', 'formatting', etc.
    severity: ValidationResult
    message: str
    location: str  # Where in the content the issue was found
    suggestions: List[str]

class ContentValidationService:
    """Service for validating textbook content for technical accuracy and reproducibility."""

    def __init__(self):
        self.validation_rules = self._load_validation_rules()

    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules for technical accuracy."""
        return {
            'technical_accuracy': {
                'forbidden_patterns': [
                    r'(?i)obviously',
                    r'(?i)clearly',
                    r'(?i)easily',
                    r'(?i)simply',
                    r'(?i)just',
                    r'(?i)it can be shown that',
                    r'(?i)it follows that'
                ],
                'required_patterns': [
                    r'(?i)proof',
                    r'(?i)derivation',
                    r'(?i)calculation',
                    r'(?i)evidence',
                    r'(?i)reference',
                    r'(?i)source'
                ],
                'technical_terms': [
                    'algorithm',
                    'function',
                    'method',
                    'theorem',
                    'lemma',
                    'corollary',
                    'proof',
                    'equation',
                    'formula',
                    'model',
                    'system',
                    'architecture',
                    'protocol',
                    'framework',
                    'approach'
                ]
            },
            'reproducibility': {
                'required_elements': [
                    'dependencies',
                    'version',
                    'environment',
                    'setup',
                    'execution',
                    'expected_output'
                ],
                'forbidden_elements': [
                    'magic_number',
                    'hardcoded_value',
                    'assumption_without_justification'
                ]
            },
            'formatting': {
                'required_patterns': [
                    r'## Learning Outcomes',
                    r'## Exercises',
                    r'## Review Questions'
                ]
            }
        }

    def validate_chapter_content(self, content: str, chapter_title: str = "") -> List[ValidationIssue]:
        """Validate a chapter's content for technical accuracy."""
        issues = []

        # Check for technical accuracy issues
        issues.extend(self._validate_technical_accuracy(content, chapter_title))

        # Check for reproducibility issues
        issues.extend(self._validate_reproducibility(content))

        # Check for formatting issues
        issues.extend(self._validate_formatting(content))

        return issues

    def _validate_technical_accuracy(self, content: str, chapter_title: str) -> List[ValidationIssue]:
        """Validate content for technical accuracy."""
        issues = []

        # Check for vague language that might indicate lack of technical accuracy
        for pattern in self.validation_rules['technical_accuracy']['forbidden_patterns']:
            matches = re.finditer(pattern, content)
            for match in matches:
                issues.append(ValidationIssue(
                    id=f"ta_{len(issues)+1}",
                    type="technical_accuracy",
                    severity=ValidationResult.WARNING,
                    message=f"Potentially vague language detected: '{match.group()}'",
                    location=f"Position {match.start()}-{match.end()} in content",
                    suggestions=["Replace with specific technical terms", "Provide evidence or derivation"]
                ))

        # Check for required technical terms
        content_lower = content.lower()
        has_technical_terms = any(term in content_lower for term in
                                 self.validation_rules['technical_accuracy']['technical_terms'])

        if not has_technical_terms and chapter_title.lower() != 'introduction':
            issues.append(ValidationIssue(
                id=f"ta_{len(issues)+1}",
                type="technical_accuracy",
                severity=ValidationResult.WARNING,
                message="Content may lack sufficient technical terminology",
                location="Entire chapter",
                suggestions=["Include more technical terms", "Add specific algorithms, methods, or systems"]
            ))

        return issues

    def _validate_reproducibility(self, content: str) -> List[ValidationIssue]:
        """Validate code examples and exercises for reproducibility."""
        issues = []

        # Look for code blocks and validate them
        code_blocks = re.findall(r'```.*?\n(.*?)```', content, re.DOTALL)

        for i, code_block in enumerate(code_blocks):
            # Check if code block has language specified
            if not re.match(r'```(\w+)', content.split('```')[2*i+1] if 2*i+1 < content.count('```') else ''):
                issues.append(ValidationIssue(
                    id=f"rep_{len(issues)+1}",
                    type="reproducibility",
                    severity=ValidationResult.WARNING,
                    message=f"Code block {i+1} missing language specification",
                    location=f"Code block {i+1}",
                    suggestions=["Specify the programming language", "Use proper syntax highlighting"]
                ))

            # Check for common reproducibility issues
            if 'import' in code_block.lower() and 'pip install' not in content.lower():
                issues.append(ValidationIssue(
                    id=f"rep_{len(issues)+1}",
                    type="reproducibility",
                    severity=ValidationResult.FAIL,
                    message=f"Code block {i+1} has imports but no dependency installation instructions",
                    location=f"Code block {i+1}",
                    suggestions=["Add dependency installation instructions", "Include requirements.txt reference"]
                ))

        # Look for exercises and validate them
        exercise_sections = re.findall(r'## Exercises\n(.*?)(?=## |\Z)', content, re.DOTALL)
        for i, exercise_section in enumerate(exercise_sections):
            # Check if exercises have difficulty levels or expected outcomes
            if not re.search(r'(easy|medium|hard|beginner|intermediate|advanced)', exercise_section, re.IGNORECASE):
                issues.append(ValidationIssue(
                    id=f"rep_{len(issues)+1}",
                    type="reproducibility",
                    severity=ValidationResult.WARNING,
                    message=f"Exercise section {i+1} missing difficulty indicators",
                    location=f"Exercise section {i+1}",
                    suggestions=["Add difficulty levels", "Include expected learning outcomes"]
                ))

        return issues

    def _validate_formatting(self, content: str) -> List[ValidationIssue]:
        """Validate content structure and formatting."""
        issues = []

        required_sections = self.validation_rules['formatting']['required_patterns']

        for section in required_sections:
            if not re.search(section, content, re.IGNORECASE):
                issues.append(ValidationIssue(
                    id=f"fmt_{len(issues)+1}",
                    type="formatting",
                    severity=ValidationResult.FAIL,
                    message=f"Required section missing: {section}",
                    location="Entire chapter",
                    suggestions=[f"Add the {section} section"]
                ))

        return issues

    def validate_code_example(self, code: str, language: str = "python") -> List[ValidationIssue]:
        """Validate a specific code example for technical accuracy and reproducibility."""
        issues = []

        # Basic syntax validation for Python
        if language.lower() in ['python', 'py']:
            # Check for basic syntax errors
            try:
                ast.parse(code)
            except SyntaxError as e:
                issues.append(ValidationIssue(
                    id=f"code_{len(issues)+1}",
                    type="reproducibility",
                    severity=ValidationResult.FAIL,
                    message=f"Syntax error in code: {str(e)}",
                    location="Code example",
                    suggestions=["Fix syntax error", "Verify code follows Python syntax"]
                ))

            # Check for undefined variables
            try:
                tree = ast.parse(code)
                defined_vars = set()
                used_vars = set()

                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                defined_vars.add(target.id)
                    elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                        used_vars.add(node.id)

                # Common built-ins to exclude
                builtins = {'print', 'len', 'range', 'int', 'str', 'float', 'list', 'dict', 'set', 'tuple', 'True', 'False', 'None', 'abs', 'max', 'min', 'sum', 'round', 'input', 'open', 'enumerate', 'zip', 'map', 'filter', 'sorted', 'reversed', 'all', 'any', 'isinstance', 'type', 'id', 'help', 'dir', 'hasattr', 'getattr', 'setattr', 'delattr', 'callable', 'iter', 'next', 'pow', 'divmod', 'complex', 'bool', 'ord', 'chr', 'hex', 'oct', 'bin', 'ascii', 'repr', 'format', 'locals', 'globals', 'vars', 'super', 'property', 'staticmethod', 'classmethod', 'slice', 'object', 'memoryview', 'bytes', 'bytearray', 'frozenset', 'Exception', 'ValueError', 'TypeError', 'IndexError', 'KeyError', 'AttributeError', 'ImportError', 'ModuleNotFoundError', 'NameError', 'SyntaxError', 'IndentationError', 'ZeroDivisionError', 'OverflowError', 'RuntimeError', 'StopIteration', 'StopAsyncIteration', 'ArithmeticError', 'AssertionError', 'AttributeError', 'BufferError', 'EOFError', 'FloatingPointError', 'GeneratorExit', 'ImportError', 'ModuleNotFoundError', 'LookupError', 'MemoryError', 'NameError', 'OSError', 'ReferenceError', 'RuntimeError', 'StopIteration', 'StopAsyncIteration', 'SystemError', 'SystemExit', 'TabError', 'TypeError', 'UnboundLocalError', 'UnicodeError', 'UnicodeDecodeError', 'UnicodeEncodeError', 'UnicodeTranslateError', 'ValueError', 'ZeroDivisionError'}

                undefined_vars = used_vars - defined_vars - builtins
                for var in undefined_vars:
                    if len(var) > 1:  # Ignore single letters like loop variables
                        issues.append(ValidationIssue(
                            id=f"code_{len(issues)+1}",
                            type="reproducibility",
                            severity=ValidationResult.FAIL,
                            message=f"Potential undefined variable: {var}",
                            location="Code example",
                            suggestions=[f"Define variable {var} before use", f"Check if {var} is a typo"]
                        ))
            except SyntaxError:
                # Already caught above
                pass

        return issues

    def execute_code_example(self, code: str, language: str = "python", timeout: int = 10) -> Dict[str, Any]:
        """Execute a code example and return the results."""
        if language.lower() not in ['python', 'py']:
            return {
                'success': False,
                'error': f'Execution not supported for language: {language}',
                'output': '',
                'execution_time': 0
            }

        # Create a temporary file to execute the code safely
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name

        try:
            # Execute the code with a timeout
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return {
                'success': result.returncode == 0,
                'error': result.stderr if result.returncode != 0 else '',
                'output': result.stdout,
                'execution_time': result.time if hasattr(result, 'time') else 0
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f'Code execution timed out after {timeout} seconds',
                'output': '',
                'execution_time': timeout
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'output': '',
                'execution_time': 0
            }
        finally:
            # Clean up the temporary file
            os.unlink(temp_file)

    def validate_exercises(self, exercises: List[Dict[str, Any]]) -> List[ValidationIssue]:
        """Validate exercise definitions for completeness and correctness."""
        issues = []

        for i, exercise in enumerate(exercises):
            # Check if exercise has required fields
            required_fields = ['question', 'type']
            for field in required_fields:
                if field not in exercise:
                    issues.append(ValidationIssue(
                        id=f"ex_{len(issues)+1}",
                        type="reproducibility",
                        severity=ValidationResult.FAIL,
                        message=f"Exercise {i+1} missing required field: {field}",
                        location=f"Exercise {i+1}",
                        suggestions=[f"Add the {field} field to the exercise"]
                    ))

            # Check if difficulty is specified
            if 'difficulty' not in exercise:
                issues.append(ValidationIssue(
                    id=f"ex_{len(issues)+1}",
                    type="reproducibility",
                    severity=ValidationResult.WARNING,
                    message=f"Exercise {i+1} missing difficulty level",
                    location=f"Exercise {i+1}",
                    suggestions=["Add difficulty level (easy/medium/hard)"]
                ))

            # Validate code-based exercises
            if exercise.get('type') == 'coding' and 'solution' in exercise:
                solution_code = exercise['solution']
                code_issues = self.validate_code_example(solution_code)
                for issue in code_issues:
                    issue.id = f"ex_{issue.id}"
                    issue.location = f"Exercise {i+1} solution"
                    issues.append(issue)

        return issues

    def validate_code_examples_in_content(self, content: str) -> List[ValidationIssue]:
        """Extract and validate all code examples in the content."""
        issues = []

        # Extract code blocks with language specification
        code_blocks = re.findall(r'```(\w+)?\n(.*?)```', content, re.DOTALL)

        for i, (lang, code) in enumerate(code_blocks):
            language = lang if lang else "python"  # Default to Python

            # Validate the code
            code_issues = self.validate_code_example(code, language)
            for issue in code_issues:
                issue.id = f"content_{issue.id}"
                issue.location = f"Code block {i+1} in content"
                issues.append(issue)

        return issues

    def validate_learning_outcomes(self, learning_outcomes: List[str]) -> List[ValidationIssue]:
        """Validate learning outcomes for completeness and measurability."""
        issues = []

        if not learning_outcomes:
            issues.append(ValidationIssue(
                id=f"lo_{len(issues)+1}",
                type="content_completeness",
                severity=ValidationResult.FAIL,
                message="No learning outcomes defined",
                location="Chapter learning outcomes",
                suggestions=["Add at least 3-5 specific learning outcomes", "Use action verbs like 'define', 'explain', 'analyze', 'implement'"]
            ))
        else:
            for i, outcome in enumerate(learning_outcomes):
                # Check if learning outcome is specific and measurable
                if len(outcome.strip()) < 10:
                    issues.append(ValidationIssue(
                        id=f"lo_{len(issues)+1}",
                        type="content_quality",
                        severity=ValidationResult.WARNING,
                        message=f"Learning outcome {i+1} is too brief: '{outcome[:30]}...'",
                        location=f"Learning outcome {i+1}",
                        suggestions=["Expand the learning outcome to be more specific", "Include measurable action verbs"]
                    ))

                # Check for action verbs
                action_verbs = [
                    'define', 'describe', 'explain', 'analyze', 'evaluate', 'compare', 'contrast',
                    'apply', 'implement', 'design', 'create', 'solve', 'calculate', 'demonstrate',
                    'identify', 'recognize', 'classify', 'summarize', 'interpret', 'assess'
                ]

                has_action_verb = any(verb in outcome.lower() for verb in action_verbs)
                if not has_action_verb:
                    issues.append(ValidationIssue(
                        id=f"lo_{len(issues)+1}",
                        type="content_quality",
                        severity=ValidationResult.WARNING,
                        message=f"Learning outcome {i+1} may lack action verb: '{outcome[:50]}...'",
                        location=f"Learning outcome {i+1}",
                        suggestions=["Start with an action verb", "Use measurable terms like 'define', 'explain', 'analyze', etc."]
                    ))

                # Check for measurability
                vague_terms = [
                    'understand', 'know', 'appreciate', 'feel', 'believe', 'think',
                    'awareness', 'familiarity', 'general idea'
                ]

                has_vague_term = any(term in outcome.lower() for term in vague_terms)
                if has_vague_term:
                    issues.append(ValidationIssue(
                        id=f"lo_{len(issues)+1}",
                        type="content_quality",
                        severity=ValidationResult.WARNING,
                        message=f"Learning outcome {i+1} contains vague term: '{outcome[:50]}...'",
                        location=f"Learning outcome {i+1}",
                        suggestions=["Replace vague terms with measurable actions", "Use specific, observable outcomes"]
                    ))

        return issues

    def validate_diagram_integration(self, content: str, diagrams: List[str]) -> List[ValidationIssue]:
        """Validate that diagrams are properly integrated in the content."""
        issues = []

        for i, diagram in enumerate(diagrams):
            # Check if diagram file exists in content
            if diagram and diagram not in content:
                issues.append(ValidationIssue(
                    id=f"diag_{len(issues)+1}",
                    type="content_integrity",
                    severity=ValidationResult.FAIL,
                    message=f"Diagram reference '{diagram}' defined but not used in content",
                    location=f"Diagram {i+1} reference",
                    suggestions=[f"Add the diagram to the content using ![Alt text]({diagram})", "Remove unused diagram reference"]
                ))

            # Check if diagram has proper alt text in content
            diagram_pattern = rf'!\[(.*?)\]\({re.escape(diagram)}\)'
            matches = re.findall(diagram_pattern, content)
            if matches:
                for alt_text in matches:
                    if not alt_text or len(alt_text.strip()) < 2:
                        issues.append(ValidationIssue(
                            id=f"diag_{len(issues)+1}",
                            type="accessibility",
                            severity=ValidationResult.WARNING,
                            message=f"Diagram '{diagram}' has insufficient alt text: '{alt_text}'",
                            location=f"Diagram {i+1} usage in content",
                            suggestions=["Add descriptive alt text", "Ensure alt text describes the diagram's content and purpose"]
                        ))
            else:
                # Check if diagram is referenced in other common ways
                if diagram in content:
                    # Diagram is referenced but not using standard markdown format
                    issues.append(ValidationIssue(
                        id=f"diag_{len(issues)+1}",
                        type="formatting",
                        severity=ValidationResult.WARNING,
                        message=f"Diagram '{diagram}' referenced but not using standard markdown format",
                        location=f"Diagram {i+1} reference in content",
                        suggestions=["Use standard markdown format: ![Description](filename.png)", "Ensure consistent diagram referencing"]
                    ))

        # Check for diagrams mentioned in content but not defined
        content_diagram_refs = re.findall(r'!\[([^\]]*)\]\(([^\)]+)\)', content)
        for alt_text, diagram_ref in content_diagram_refs:
            if diagram_ref not in diagrams:
                issues.append(ValidationIssue(
                    id=f"diag_{len(issues)+1}",
                    type="content_integrity",
                    severity=ValidationResult.WARNING,
                    message=f"Diagram '{diagram_ref}' referenced in content but not defined in chapter metadata",
                    location="Diagram reference in content",
                    suggestions=["Add the diagram to chapter metadata", "Verify diagram file exists in assets"]
                ))

        return issues

    def validate_exercises_functionality(self, exercises: List[Dict[str, Any]], content: str) -> List[ValidationIssue]:
        """Validate exercise functionality and proper integration in content."""
        issues = []

        if not exercises:
            issues.append(ValidationIssue(
                id=f"ex_{len(issues)+1}",
                type="content_completeness",
                severity=ValidationResult.WARNING,
                message="No exercises defined",
                location="Chapter exercises",
                suggestions=["Add exercises to reinforce learning outcomes", "Include a mix of difficulty levels and types"]
            ))
        else:
            for i, exercise in enumerate(exercises):
                # Validate required fields
                if 'question' not in exercise:
                    issues.append(ValidationIssue(
                        id=f"ex_{len(issues)+1}",
                        type="content_completeness",
                        severity=ValidationResult.FAIL,
                        message=f"Exercise {i+1} missing required 'question' field",
                        location=f"Exercise {i+1}",
                        suggestions=["Add the question text", "Ensure question is clear and specific"]
                    ))

                if 'type' not in exercise:
                    issues.append(ValidationIssue(
                        id=f"ex_{len(issues)+1}",
                        type="content_structure",
                        severity=ValidationResult.FAIL,
                        message=f"Exercise {i+1} missing required 'type' field",
                        location=f"Exercise {i+1}",
                        suggestions=["Specify the exercise type (e.g., 'analysis', 'design', 'research', 'coding')"]
                    ))

                # Validate exercise type
                valid_types = ['analysis', 'design', 'research', 'coding', 'application', 'evaluation', 'synthesis']
                if exercise.get('type') not in valid_types:
                    issues.append(ValidationIssue(
                        id=f"ex_{len(issues)+1}",
                        type="content_structure",
                        severity=ValidationResult.WARNING,
                        message=f"Exercise {i+1} has unrecognized type: '{exercise.get('type')}'",
                        location=f"Exercise {i+1}",
                        suggestions=[f"Use one of the valid types: {', '.join(valid_types)}", "Or update the validation rules to include your type"]
                    ))

                # Validate difficulty level
                valid_difficulties = ['easy', 'medium', 'hard', 'beginner', 'intermediate', 'advanced']
                if 'difficulty' in exercise and exercise['difficulty'] not in valid_difficulties:
                    issues.append(ValidationIssue(
                        id=f"ex_{len(issues)+1}",
                        type="content_structure",
                        severity=ValidationResult.WARNING,
                        message=f"Exercise {i+1} has unrecognized difficulty: '{exercise['difficulty']}'",
                        location=f"Exercise {i+1}",
                        suggestions=[f"Use one of the valid difficulties: {', '.join(valid_difficulties)}"]
                    ))

                # Validate question content
                question = exercise.get('question', '')
                if len(question.strip()) < 10:
                    issues.append(ValidationIssue(
                        id=f"ex_{len(issues)+1}",
                        type="content_quality",
                        severity=ValidationResult.WARNING,
                        message=f"Exercise {i+1} question is too brief: '{question[:50]}...'",
                        location=f"Exercise {i+1} question",
                        suggestions=["Expand the question to be more detailed", "Ensure the question is specific and actionable"]
                    ))

                # For coding exercises, validate solution if present
                if exercise.get('type') == 'coding' and 'solution' in exercise:
                    solution_code = exercise['solution']
                    code_issues = self.validate_code_example(solution_code)
                    for code_issue in code_issues:
                        code_issue.id = f"ex_{code_issue.id}"
                        code_issue.location = f"Exercise {i+1} solution"
                        issues.append(code_issue)

                # Check if exercise is referenced in the content
                question_snippet = question.lower()[:50].replace(' ', '_').replace('.', '').replace(',', '')
                if question_snippet not in content.lower():
                    # This is a warning because exercises don't necessarily need to be referenced in content
                    issues.append(ValidationIssue(
                        id=f"ex_{len(issues)+1}",
                        type="content_integration",
                        severity=ValidationResult.WARNING,
                        message=f"Exercise {i+1} question not found in content",
                        location=f"Exercise {i+1}",
                        suggestions=["Reference the exercise in the content", "Ensure exercises align with content covered"]
                    ))

                # Check if exercise relates to learning outcomes
                if 'learning_outcome_alignment' not in exercise:
                    issues.append(ValidationIssue(
                        id=f"ex_{len(issues)+1}",
                        type="content_alignment",
                        severity=ValidationResult.WARNING,
                        message=f"Exercise {i+1} lacks learning outcome alignment",
                        location=f"Exercise {i+1}",
                        suggestions=["Specify which learning outcomes the exercise addresses", "Ensure exercises reinforce specific learning objectives"]
                    ))

        return issues

# Example usage:
# validator = ContentValidationService()
# issues = validator.validate_chapter_content(content, "Physical AI Fundamentals")
# for issue in issues:
#     print(f"{issue.severity.value.upper()}: {issue.message} at {issue.location}")