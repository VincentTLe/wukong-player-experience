"""Build, execute, and export the main notebook using this Python environment."""
import asyncio
import json
import os
from pathlib import Path
import sys
import tempfile

import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter

ROOT = Path(__file__).resolve().parents[1]


def build_notebook():
    """The readable # %% source is the single place to edit notebook content."""
    source = ROOT / 'notebooks/wukong_player_experience.py'
    cells, lines, markdown = [], [], False

    def append_cell():
        content = '\n'.join(lines).strip()
        if content:
            factory = nbformat.v4.new_markdown_cell if markdown else nbformat.v4.new_code_cell
            cells.append(factory(content))

    for line in source.read_text(encoding='utf-8').splitlines():
        if line.startswith('# %%'):
            append_cell()
            lines = []
            markdown = '[markdown]' in line
        elif markdown:
            lines.append(line[2:] if line.startswith('# ') else line.removeprefix('#'))
        else:
            lines.append(line)
    append_cell()
    notebook = nbformat.v4.new_notebook(cells=cells)
    # Stable cell IDs keep later Git diffs focused on actual changes.
    for index, cell in enumerate(notebook.cells):
        cell.id = f'wukong-{index:02d}'
    notebook.metadata['kernelspec'] = {'name': 'python3', 'display_name': 'Python 3', 'language': 'python'}
    return notebook


def main():
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    notebook = build_notebook()
    output = ROOT / 'notebooks/wukong_player_experience.ipynb'
    print('Executing the notebook from published inputs...', flush=True)

    # A temporary kernelspec ensures execution uses this environment, not a user's default kernel.
    with tempfile.TemporaryDirectory(prefix='wukong-kernel-') as directory:
        kernel = Path(directory) / 'kernels/python3'
        kernel.mkdir(parents=True)
        (kernel / 'kernel.json').write_text(json.dumps({
            'argv': [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}'],
            'display_name': 'Python 3', 'language': 'python'
        }), encoding='utf-8')
        previous = os.environ.get('JUPYTER_PATH')
        os.environ['JUPYTER_PATH'] = directory + (os.pathsep + previous if previous else '')
        try:
            NotebookClient(notebook, timeout=300, kernel_name='python3',
                           resources={'metadata': {'path': str(ROOT)}}).execute()
        finally:
            if previous is None:
                os.environ.pop('JUPYTER_PATH', None)
            else:
                os.environ['JUPYTER_PATH'] = previous

    # Execution timing is not part of the result and creates noisy version-control diffs.
    for cell in notebook.cells:
        cell.metadata.pop('execution', None)
    nbformat.write(notebook, output)
    exporter = HTMLExporter(template_name='lab')
    body, _ = exporter.from_notebook_node(notebook, resources={'metadata': {'name': 'Beyond the Thumbs-Up'}})
    style = '''<style>
    body { background: #f7f8fb; color: #192b40; }
    main { max-width: 1060px; margin: 32px auto; background: white; padding: 36px; }
    .jp-RenderedHTMLCommon { font-family: system-ui, sans-serif; font-size: 16px; line-height: 1.65; }
    .jp-RenderedHTMLCommon h1, .jp-RenderedHTMLCommon h2 { color: #173e50; }
    .jp-RenderedHTMLCommon blockquote { border-left: 4px solid #137c80; background: #edf6f5; padding: 12px 20px; }
    .jp-InputArea-editor { border-radius: 6px; }
    .jp-InputPrompt, .jp-OutputPrompt { min-width: 42px; }
    .jp-RenderedHTMLCommon table { font-size: 14px; }
    @media (max-width: 720px) { main { padding: 12px; margin: 0; } }
    </style>'''
    body = body.replace('</head>', style + '</head>')
    report = ROOT / 'reports/wukong_player_experience.html'
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(body, encoding='utf-8', newline='\n')
    print(f'Saved {output.relative_to(ROOT)} and {report.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
