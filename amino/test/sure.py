from amino.test.sure_ext import install_assertion_builder, AssBuilder


class SureSpec:

    def setup(self) -> None:
        install_assertion_builder(AssBuilder)

__all__ = ('SureSpec',)
