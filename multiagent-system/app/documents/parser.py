"""
Parser multimodal para documentos de entrada
Soporta: PDF, DOCX, MD, imágenes (con OCR)
"""
import os
import base64
from typing import List, Dict, Any, Optional
from pathlib import Path


class DocumentParser:
    """Parser para múltiples formatos de documento"""
    
    def __init__(self, input_dir: str = "/app/input_docs"):
        self.input_dir = Path(input_dir)
        self.supported_extensions = {
            '.pdf': self._parse_pdf,
            '.docx': self._parse_docx,
            '.md': self._parse_markdown,
            '.txt': self._parse_text,
            '.png': self._parse_image,
            '.jpg': self._parse_image,
            '.jpeg': self._parse_image,
        }
    
    async def parse_all_documents(self) -> List[Dict[str, Any]]:
        """
        Parsea todos los documentos en el directorio de entrada
        
        Returns:
            Lista de diccionarios con: {filename, content, type, metadata}
        """
        documents = []
        
        if not self.input_dir.exists():
            return documents
        
        for file_path in self.input_dir.iterdir():
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in self.supported_extensions:
                    try:
                        parser_func = self.supported_extensions[ext]
                        content = await parser_func(file_path)
                        documents.append({
                            "filename": file_path.name,
                            "content": content,
                            "type": self._get_type_from_extension(ext),
                            "path": str(file_path),
                            "size": file_path.stat().st_size
                        })
                    except Exception as e:
                        print(f"Error parsing {file_path.name}: {str(e)}")
        
        return documents
    
    async def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Parsea un archivo específico"""
        path = Path(file_path)
        ext = path.suffix.lower()
        
        if ext not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {ext}")
        
        parser_func = self.supported_extensions[ext]
        content = await parser_func(path)
        
        return {
            "filename": path.name,
            "content": content,
            "type": self._get_type_from_extension(ext),
            "path": str(path),
            "size": path.stat().st_size
        }
    
    async def _parse_pdf(self, file_path: Path) -> str:
        """Extrae texto de PDF"""
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(str(file_path))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error parsing PDF: {str(e)}")
    
    async def _parse_docx(self, file_path: Path) -> str:
        """Extrae texto de DOCX"""
        try:
            from docx import Document
            doc = Document(str(file_path))
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            raise Exception(f"Error parsing DOCX: {str(e)}")
    
    async def _parse_markdown(self, file_path: Path) -> str:
        """Lee archivo Markdown"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            raise Exception(f"Error parsing Markdown: {str(e)}")
    
    async def _parse_text(self, file_path: Path) -> str:
        """Lee archivo de texto plano"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            raise Exception(f"Error parsing text: {str(e)}")
    
    async def _parse_image(self, file_path: Path) -> str:
        """
        Extrae texto de imagen usando OCR
        Requiere tesseract-ocr instalado
        """
        try:
            import pytesseract
            from PIL import Image
            
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image, lang='eng+spa')
            return text.strip()
        except Exception as e:
            # Si falla OCR, devolver información básica
            return f"[Imagen: {file_path.name}] - OCR no disponible: {str(e)}"
    
    def _get_type_from_extension(self, ext: str) -> str:
        """Obtiene el tipo de documento desde la extensión"""
        type_map = {
            '.pdf': 'pdf',
            '.docx': 'document',
            '.md': 'markdown',
            '.txt': 'text',
            '.png': 'image',
            '.jpg': 'image',
            '.jpeg': 'image',
        }
        return type_map.get(ext, 'unknown')
    
    async def get_summary(self, max_length: int = 1000) -> str:
        """
        Genera un resumen de todos los documentos
        
        Args:
            max_length: Longitud máxima del resumen
            
        Returns:
            Resumen concatenado de todos los documentos
        """
        documents = await self.parse_all_documents()
        
        if not documents:
            return "No documents found in input directory."
        
        summary_parts = []
        total_length = 0
        
        for doc in documents:
            content_preview = doc['content'][:300] + "..." if len(doc['content']) > 300 else doc['content']
            summary_parts.append(f"📄 **{doc['filename']}** ({doc['type']}):\n{content_preview}")
            total_length += len(summary_parts[-1])
            
            if total_length >= max_length:
                break
        
        return "\n\n---\n\n".join(summary_parts)


async def parse_uploaded_file(file_content: bytes, filename: str) -> Dict[str, Any]:
    """
    Parsea un archivo subido directamente (no desde directorio)
    
    Args:
        file_content: Contenido binario del archivo
        filename: Nombre del archivo
        
    Returns:
        Diccionario con la información del documento
    """
    from pathlib import Path
    import tempfile
    
    ext = Path(filename).suffix.lower()
    parser = DocumentParser()
    
    if ext not in parser.supported_extensions:
        raise ValueError(f"Unsupported file type: {ext}")
    
    # Guardar temporalmente
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp_file:
        tmp_file.write(file_content)
        tmp_path = Path(tmp_file.name)
    
    try:
        parser_func = parser.supported_extensions[ext]
        content = await parser_func(tmp_path)
        
        return {
            "filename": filename,
            "content": content,
            "type": parser._get_type_from_extension(ext),
            "size": len(file_content)
        }
    finally:
        # Limpiar archivo temporal
        tmp_path.unlink(missing_ok=True)
