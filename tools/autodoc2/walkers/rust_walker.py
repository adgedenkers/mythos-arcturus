"""
Rust walker using tree-sitter.

Extracts:
  - function_item     -> ParsedFunction (top-level fn)
  - struct_item       -> ParsedClass with __struct__ tag
  - enum_item         -> ParsedClass with __enum__ tag
  - trait_item        -> ParsedClass with __trait__ tag
  - union_item        -> ParsedClass with __union__ tag
  - type_item         -> ParsedClass with __type_alias__ tag
  - impl_item         -> walked for inner function_items, attached to the
                         implemented type as parent_class. So:
                            impl Foo { fn bar() {} }
                         produces a Function 'bar' with parent_class='Foo'.
  - use_declaration   -> ParsedImport
  - call_expression in function bodies -> calls list

Mod handling: nested mod blocks (`mod foo { ... }`) prefix the qualified name
with the mod path. We track the mod stack as we walk.

Resilient to syntax errors.
"""
from pathlib import Path
from typing import List, Optional
from ..walker import (
    LanguageWalker,
    ParsedFile,
    ParsedClass,
    ParsedFunction,
    ParsedImport,
)


class RustWalker(LanguageWalker):
    language = "rust"
    grammar_key = "rust"

    def __init__(self):
        try:
            from tree_sitter_language_pack import get_parser
            self._parser = get_parser(self.grammar_key)
            self._available = True
            self._init_error = None
        except Exception as e:
            self._parser = None
            self._available = False
            self._init_error = str(e)

    def parse_file(self, path: Path, relative_path: str, source: bytes) -> ParsedFile:
        self._source = source
        pf = ParsedFile(
            path=path,
            relative_path=relative_path,
            language=self.language,
            line_count=source.count(b'\n') + 1,
        )
        if not self._available:
            pf.parse_errors.append(f"tree-sitter not available: {self._init_error}")
            return pf
        try:
            tree = self._parser.parse(source)
        except Exception as e:
            pf.parse_errors.append(f"parse failed: {e}")
            return pf

        root = tree.root_node
        module_name = self._module_name_from_path(relative_path)
        # Walk top-level items, tracking the mod path stack
        self._walk_items(root, pf, module_name, mod_path=[], parent_impl=None)
        return pf

    @staticmethod
    def _module_name_from_path(relative_path: str) -> str:
        p = relative_path.replace('\\', '/')
        if p.endswith('.rs'):
            p = p[:-3]
        return p.replace('/', '.')

    def _text(self, node) -> str:
        return self._source[node.start_byte:node.end_byte].decode('utf-8', errors='replace')

    def _qual(self, module_name: str, mod_path: List[str], name: str) -> str:
        parts = [module_name] + mod_path + [name]
        return '.'.join(parts)

    def _walk_items(self, node, pf: ParsedFile, module_name: str,
                    mod_path: List[str], parent_impl: Optional[str]):
        """Walk children of `node` looking for top-level items.
        `parent_impl`: when we're inside an impl block, this is the type name
        the impl is for. Functions found inside become methods of that type.
        """
        for child in node.children:
            t = child.type

            if t == 'function_item':
                self._handle_function(child, pf, module_name, mod_path, parent_impl)

            elif t == 'struct_item':
                self._handle_typedef(child, pf, module_name, mod_path, kind='struct')

            elif t == 'enum_item':
                self._handle_typedef(child, pf, module_name, mod_path, kind='enum')

            elif t == 'union_item':
                self._handle_typedef(child, pf, module_name, mod_path, kind='union')

            elif t == 'trait_item':
                self._handle_typedef(child, pf, module_name, mod_path, kind='trait')
                # trait bodies can contain function_item declarations — walk for those
                body = child.child_by_field_name('body')
                if body is not None:
                    trait_name = self._extract_name(child)
                    if trait_name:
                        self._walk_items(body, pf, module_name, mod_path,
                                         parent_impl=trait_name)

            elif t == 'type_item':
                self._handle_typedef(child, pf, module_name, mod_path, kind='type_alias')

            elif t == 'impl_item':
                self._handle_impl(child, pf, module_name, mod_path)

            elif t == 'mod_item':
                self._handle_mod(child, pf, module_name, mod_path)

            elif t == 'use_declaration':
                self._handle_use(child, pf)

            elif t in ('source_file', 'declaration_list'):
                # Wrapping nodes — recurse
                self._walk_items(child, pf, module_name, mod_path, parent_impl)

    def _extract_name(self, item_node) -> Optional[str]:
        name_node = item_node.child_by_field_name('name')
        if name_node is None:
            for ch in item_node.children:
                if ch.type in ('identifier', 'type_identifier'):
                    name_node = ch
                    break
        if name_node is None:
            return None
        return self._text(name_node).strip()

    def _handle_function(self, node, pf: ParsedFile, module_name: str,
                         mod_path: List[str], parent_impl: Optional[str]):
        fn_name = self._extract_name(node)
        if not fn_name:
            return
        is_async = self._is_async(node)
        if parent_impl:
            qualified = self._qual(module_name, mod_path, f"{parent_impl}.{fn_name}")
        else:
            qualified = self._qual(module_name, mod_path, fn_name)
        pf.functions.append(ParsedFunction(
            name=fn_name,
            qualified_name=qualified,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            is_async=is_async,
            is_method=parent_impl is not None,
            parent_class=parent_impl,
            docstring=None,
            calls=self._extract_calls(node),
        ))

    def _is_async(self, node) -> bool:
        # Rust async fn: the 'async' modifier appears as a child token before 'fn'
        for ch in node.children:
            if ch.type == 'function_modifiers':
                if 'async' in self._text(ch):
                    return True
            if ch.type == 'async':
                return True
        return False

    def _handle_typedef(self, node, pf: ParsedFile, module_name: str,
                        mod_path: List[str], kind: str):
        name = self._extract_name(node)
        if not name:
            return
        pf.classes.append(ParsedClass(
            name=name,
            qualified_name=self._qual(module_name, mod_path, name),
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            bases=[f"__{kind}__"],
            docstring=None,
        ))

    def _handle_impl(self, node, pf: ParsedFile, module_name: str,
                     mod_path: List[str]):
        """impl Foo { ... } or impl Trait for Foo { ... }
        Either way, methods inside attach to Foo as parent_class.
        """
        # The 'type' field is the type being implemented for
        type_node = node.child_by_field_name('type')
        if type_node is None:
            # Walk children for the first type_identifier
            for ch in node.children:
                if ch.type in ('type_identifier', 'generic_type', 'scoped_type_identifier'):
                    type_node = ch
                    break
        if type_node is None:
            return
        impl_for = self._text(type_node).strip()
        # Strip generics like Foo<T> -> Foo
        if '<' in impl_for:
            impl_for = impl_for.split('<', 1)[0].strip()

        body = node.child_by_field_name('body')
        if body is None:
            for ch in node.children:
                if ch.type == 'declaration_list':
                    body = ch
                    break
        if body is not None:
            self._walk_items(body, pf, module_name, mod_path, parent_impl=impl_for)

    def _handle_mod(self, node, pf: ParsedFile, module_name: str,
                    mod_path: List[str]):
        """mod foo { ... } — push 'foo' onto the mod_path stack and recurse."""
        mod_name = self._extract_name(node)
        if not mod_name:
            return
        body = node.child_by_field_name('body')
        if body is None:
            for ch in node.children:
                if ch.type == 'declaration_list':
                    body = ch
                    break
        if body is not None:
            new_path = mod_path + [mod_name]
            self._walk_items(body, pf, module_name, new_path, parent_impl=None)

    def _handle_use(self, node, pf: ParsedFile):
        """Parse `use foo::bar::baz;` and `use foo::{a, b, c};`
        We emit one import per use_declaration with the full path as the module.
        """
        # Walk children for scoped_identifier / scoped_use_list / identifier
        for child in node.children:
            t = child.type
            if t in ('scoped_identifier', 'identifier', 'scoped_use_list',
                     'use_list', 'use_as_clause'):
                module = self._text(child).rstrip(';').strip()
                # Convert :: to . for graph consistency
                module_dotted = module.replace('::', '.')
                if module_dotted:
                    pf.imports.append(ParsedImport(
                        module=module_dotted,
                        names=[],
                        is_relative=module_dotted.startswith('crate.')
                                    or module_dotted.startswith('self.')
                                    or module_dotted.startswith('super.'),
                        line=node.start_point[0] + 1,
                    ))
                return  # one import per use_declaration

    def _extract_calls(self, fn_node) -> List[str]:
        calls: List[str] = []
        body = fn_node.child_by_field_name('body')
        if body is None:
            return calls
        stack = [body]
        while stack:
            n = stack.pop()
            if n.type == 'call_expression':
                func = n.child_by_field_name('function')
                if func is not None:
                    name = self._text(func).strip()
                    if '\n' not in name and len(name) < 120:
                        calls.append(name)
            elif n.type == 'macro_invocation':
                # Track macro calls too: println!, vec!, etc.
                macro = n.child_by_field_name('macro')
                if macro is not None:
                    name = self._text(macro).strip()
                    if name and '\n' not in name:
                        calls.append(f"{name}!")
            for ch in n.children:
                stack.append(ch)
        return calls
