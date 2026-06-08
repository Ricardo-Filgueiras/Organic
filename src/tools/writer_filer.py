# Quero fornecer uma ferramenta para o agente escrever em um arquivo, 
# para que ele possa salvar informações importantes ou gerar relatórios. 
# A ferramenta deve ser fácil de usar e permitir que o agente escreva em 
# um arquivo de .md 
# 
# Aqui está um exemplo de como essa ferramenta pode ser implementada:

from pathlib import Path

class MarkdownWriter():
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, filename: str, content: str):
        file_path = self.file_path.parent / f'{filename}.md'
        with file_path.open('w', encoding='utf-8') as f:
            f.write(content + '\n')

        return str(file_path)