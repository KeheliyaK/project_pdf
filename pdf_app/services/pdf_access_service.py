from __future__ import annotations

import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader, PdfWriter


class PdfPasswordRequiredError(RuntimeError):
    pass


class PdfInvalidPasswordError(RuntimeError):
    pass


@dataclass(frozen=True)
class PreparedPdf:
    source_path: Path
    prepared_path: Path
    page_count: int
    was_password_protected: bool = False


class PdfAccessService:
    def __init__(self) -> None:
        self._temp_dir = Path(tempfile.mkdtemp(prefix="pdf-app-access-"))

    def prepare_pdf(
        self,
        source_path: str | Path,
        destination_path: str | Path | None = None,
        password: str | None = None,
    ) -> PreparedPdf:
        source = Path(source_path)
        target = Path(destination_path) if destination_path else self._next_temp_path(source.suffix or ".pdf")
        target.parent.mkdir(parents=True, exist_ok=True)

        reader = PdfReader(str(source))
        if reader.is_encrypted:
            if password is None:
                raise PdfPasswordRequiredError(f"{source.name} requires a password.")
            if reader.decrypt(password) == 0:
                raise PdfInvalidPasswordError(f"Incorrect password for {source.name}.")
            self._write_decrypted_copy(reader, target)
            return PreparedPdf(
                source_path=source,
                prepared_path=target,
                page_count=len(reader.pages),
                was_password_protected=True,
            )

        if source.resolve() == target.resolve():
            return PreparedPdf(
                source_path=source,
                prepared_path=target,
                page_count=len(reader.pages),
                was_password_protected=False,
            )
        shutil.copy2(source, target)
        return PreparedPdf(
            source_path=source,
            prepared_path=target,
            page_count=len(reader.pages),
            was_password_protected=False,
        )

    @staticmethod
    def _write_decrypted_copy(reader: PdfReader, output_path: Path) -> None:
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        with output_path.open("wb") as handle:
            writer.write(handle)

    def _next_temp_path(self, suffix: str) -> Path:
        fd, temp_name = tempfile.mkstemp(suffix=suffix, dir=self._temp_dir)
        os.close(fd)
        Path(temp_name).unlink(missing_ok=True)
        return Path(temp_name)
