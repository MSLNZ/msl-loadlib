from __future__ import annotations

from enum import IntEnum
from enum import IntFlag
from typing import Any

from sphinx.ext.autodoc import ClassDocumenter
from sphinx.ext.autodoc import annotation_option


class IntEnumDocumenter(ClassDocumenter):
    objtype = 'intenum'
    directivetype = ClassDocumenter.objtype
    priority = 10 + ClassDocumenter.priority
    option_spec = dict(ClassDocumenter.option_spec)
    option_spec['hex'] = annotation_option

    @classmethod
    def can_document_member(cls, member: Any, membername: str, isattr: bool, parent: Any) -> bool:
        return isinstance(member, (IntEnum, IntFlag))

    def format_signature(self, **kwargs: Any) -> str:
        # trim the default Enum signature, e.g.,
        # (value, names=None, *values, module=None, qualname=None, type=None, start=1, boundary=None)
        return '(value)'

    def document_members(self, all_members: bool = False) -> None:
        source_name = self.get_sourcename()
        hex_option = self.options.hex

        self.add_line('', source_name)

        for member in self.object:
            the_member_value = member.value
            if hex_option is not None:
                try:
                    the_member_value = f'0x{the_member_value:0{int(hex_option)}x}'
                except TypeError:
                    the_member_value = hex(the_member_value)

            self.add_line(f'.. py:attribute:: {member.name}', source_name)
            self.add_line(f'   :module: {self.modname}', source_name)
            self.add_line(f'   :value: {the_member_value}', source_name)
            self.add_line('', source_name)
