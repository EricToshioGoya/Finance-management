"""Verifica integridade documental; não executa testes da aplicação FinNova."""
from pathlib import Path
from urllib.parse import unquote, urlsplit
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
REQ = ROOT / 'docs/03-requisitos/requisitos.md'
errors = []
source = REQ.read_text(encoding='utf-8')
definitions = {}
for prefix, pattern, expected in (
    ('RF', r'^#### (RF-\d{2})\s', 74),
    ('RNF', r'^\| (RNF-\d{2}) \|', 25),
    ('RB', r'^\| (RB-\d{2}) \|', 29),
):
    ids = re.findall(pattern, source, re.MULTILINE)
    definitions[prefix] = set(ids)
    if len(ids) != expected or len(ids) != len(set(ids)):
        errors.append(f'{prefix}: IDs ausentes, duplicados ou quantidade inesperada')
    if set(ids) != {f'{prefix}-{n:02d}' for n in range(1, expected + 1)}:
        errors.append(f'{prefix}: sequência de IDs incompleta')

def collect(pattern, filename):
    return set(re.findall(pattern, (ROOT / filename).read_text(encoding='utf-8'), re.MULTILINE))

definitions['OPEN'] = collect(r'^\| (OPEN-\d{2}) \|', 'docs/08-specs/questoes-abertas.md')
definitions['DA'] = collect(r'^\| (DA-\d{2}) \|', 'docs/07-arquitetura/arquitetura.md')
definitions['SPEC'] = collect(r'^\| \d+ \| (SPEC-\d{3})\b', 'docs/08-specs/mapa-specs.md')
definitions['UC'] = set()
for name in ('usuario', 'administrador'):
    definitions['UC'].update(collect(r'^\| (UC-\d{2}) \|', f'docs/04-casos-de-uso/casos-de-uso-{name}.md'))
definitions['UC'].update(collect(r'^\| (UC-\d{2}) \|', 'docs/04-casos-de-uso/conta-acesso-complemento.md'))
definitions['ADR'] = {p.name[:7] for p in (ROOT / 'docs/07-arquitetura/adrs').glob('ADR-*.md')}

refs = re.compile(r'\b(RNF|RF|RB|OPEN|DA|UC|SPEC|ADR)-(\d{2,3})\b')
links = re.compile(r'!?\[[^\]\n]*\]\(([^\)\n]+)\)')

def slug(heading):
    heading = re.sub(r'<[^>]+>', '', heading)
    heading = heading.strip().lower().replace('`', '').replace('*', '')
    heading = re.sub(r'[^\w\- ]', '', heading, flags=re.UNICODE)
    return heading.replace(' ', '-')

files = [ROOT / 'README.md', ROOT / 'AGENTS.md']
files += list((ROOT / 'docs').rglob('*.md'))
for path in files:
    rel = path.relative_to(ROOT)
    content = path.read_text(encoding='utf-8')
    for match in refs.finditer(content):
        ident = match.group(0)
        if ident not in definitions[match.group(1)]:
            line = content[:match.start()].count('\n') + 1
            errors.append(f'{rel}:{line}: referência sem definição: {ident}')
    for match in links.finditer(content):
        target = match.group(1).strip().split(' "')[0].strip('<>')
        parts = urlsplit(target)
        if parts.scheme or parts.netloc:
            continue
        resolved = (path.parent / unquote(parts.path)).resolve() if parts.path else path.resolve()
        if not resolved.is_relative_to(ROOT.resolve()):
            errors.append(f'{rel}: link fora do repositório: {target}')
        elif not resolved.exists():
            errors.append(f'{rel}: link inexistente: {target}')
        elif parts.fragment and resolved.is_file() and resolved.suffix == '.md':
            headings = re.findall(r'^#{1,6}\s+(.+)$', resolved.read_text(encoding='utf-8'), re.MULTILINE)
            if unquote(parts.fragment) not in {slug(h) for h in headings}:
                errors.append(f'{rel}: âncora inexistente: {target}')

# Os 14 itens do PDF são necessários; o antigo subconjunto não demonstra
# conformidade estrutural. A aprovação e a correção semântica continuam humanas.
required_sections = (
    'Identificação', 'Rastreabilidade', 'Escopo', 'Dependências',
    'Comportamento esperado', 'Regras e invariantes',
    'Modelo de domínio envolvido', 'Impacto arquitetural',
    'Contratos necessários', 'Requisitos não funcionais aplicáveis',
    'Critérios de Aceitação', 'Casos de teste derivados',
    'Questões em Aberto', 'Definition of Done da Spec',
)
for name in ('SPEC-001.md', 'SPEC-002.md'):
    if not (ROOT / 'docs/08-specs' / name).is_file():
        errors.append(f'Spec individual ausente: {name}')
for path in sorted((ROOT / 'docs/08-specs').glob('SPEC-*.md')):
    content = path.read_text(encoding='utf-8')
    headings = list(re.finditer(r'^## (\d+)\. (.+)$', content, re.MULTILINE))
    titles = [m.group(2).casefold() for m in headings]
    if titles != [title.casefold() for title in required_sections] or [int(m.group(1)) for m in headings] != list(range(1, 15)):
        errors.append(f'{path.name}: são necessárias as 14 seções ordenadas do modelo SDD')
        continue
    sections = [content[m.end():headings[i+1].start() if i+1 < len(headings) else len(content)].strip() for i, m in enumerate(headings)]
    for title, body in zip(required_sections, sections):
        if not body:
            errors.append(f'{path.name}: seção vazia: {title}')
    acceptance = sections[10]
    if not all(f'**{word}**' in acceptance for word in ('Dado', 'Quando', 'Então')):
        errors.append(f'{path.name}: critérios Dado/Quando/Então ausentes')
    for prefix, source_index in (('CA', 10), ('INV', 5)):
        ids = re.findall(rf'\*\*({prefix}-\d{{3}}):?\*\*', sections[source_index])
        if not ids or len(ids) != len(set(ids)):
            errors.append(f'{path.name}: identificadores {prefix} ausentes ou duplicados')
        for ident in ids:
            if ident not in sections[11]:
                errors.append(f'{path.name}: {ident} sem teste derivado relacionado')
    if not re.search(r'^\| T-\d{3} \|', sections[11], re.MULTILINE):
        errors.append(f'{path.name}: tabela de testes derivados ausente')
    if '- [ ]' not in sections[13]:
        errors.append(f'{path.name}: checklist de Definition of Done ausente')

map_content = (ROOT / 'docs/08-specs/mapa-specs.md').read_text(encoding='utf-8')
map_rows = []
for line in map_content.splitlines():
    if re.match(r'^\| \d+ \| SPEC-\d{3}\b', line):
        cells = [cell.strip() for cell in line.strip('|').split('|')]
        map_rows.append((int(cells[0]), cells[1].split()[0], cells[-1]))
if not map_rows:
    errors.append('Mapa: nenhuma Spec encontrada')
order = {ident: position for position, ident, _ in map_rows}
if len(order) != len(map_rows) or len({position for position, _, _ in map_rows}) != len(map_rows):
    errors.append('Mapa: IDs ou posições duplicados')
for position, ident, dependencies in map_rows:
    for dep in re.findall(r'SPEC-\d{3}', dependencies):
        if dep not in order or order[dep] >= position:
            errors.append(f'Mapa: {ident} depende de {dep} fora da ordem anterior')
    detail = re.search(rf'^\| {ident} \| (.+)$', map_content, re.MULTILINE)
    if not detail or len([cell for cell in detail.group(1).strip('|').split('|') if cell.strip()]) != 3:
        errors.append(f'Mapa: {ident} sem objetivo, valor e justificativa de ordem')

for path in (ROOT / 'docs/04-casos-de-uso/seq-UC-09.mmd', ROOT / 'docs/04-casos-de-uso/estados-UC-09.mmd'):
    if not path.exists():
        errors.append(f'Fonte de diagrama ausente: {path.name}')
# Full-catalog checks: missing files/coverage/clauses must fail documentation CI.
spec_paths = {p.stem: p for p in (ROOT / 'docs/08-specs').glob('SPEC-*.md')}
if set(spec_paths) != definitions['SPEC']:
    errors.append('Catálogo: mapa e arquivos individuais de Spec divergem')
for sid, path in spec_paths.items():
    content = path.read_text(encoding='utf-8')
    if not content.startswith(f'# {sid}:'):
        errors.append(f'{sid}: identidade do título divergente')
    if re.search(r'^(<<<<<<< |=======|>>>>>>> )', content, re.MULTILINE):
        errors.append(f'{sid}: marcador de conflito de merge')
    if len(re.findall(r'^```', content, re.MULTILINE)) % 2:
        errors.append(f'{sid}: bloco de código não fechado')
    for line in content.splitlines():
        if line.startswith('| ') and f'| {sid}-R' in line:
            rid = re.search(rf'{sid}-R\d{{2}}', line)
            if rid and not re.search(rf'^\| T-[^|]+\|[^\n]*{re.escape(rid.group(0))}', content, re.MULTILINE):
                errors.append(f'{sid}: cláusula {rid.group(0)} sem teste derivado')
for prefix, filename in [('RF', 'cobertura-requisitos.md'), ('RNF', 'cobertura-rnf.md')]:
    path = ROOT / 'docs/08-specs' / filename
    if not path.is_file():
        errors.append(f'Cobertura ausente: {filename}')
        continue
    content = path.read_text(encoding='utf-8')
    ids = re.findall(rf'^\| ({prefix}-\d{{2}}) \|', content, re.MULTILINE)
    if len(ids) != len(set(ids)) or set(ids) != definitions[prefix]:
        errors.append(f'{filename}: cobertura incompleta ou duplicada')
    for line in content.splitlines():
        if re.match(rf'^\| {prefix}-\d{{2}} \|', line) and not re.search(r'\[SPEC-\d{3}\]\(SPEC-\d{3}\.md\)', line):
            errors.append(f'{filename}: requisito sem Spec responsável vinculada')
open_ids = re.findall(r'^\| (OPEN-\d{2}) \|', (ROOT / 'docs/08-specs/questoes-abertas.md').read_text(encoding='utf-8'), re.MULTILINE)
if len(open_ids) != len(set(open_ids)):
    errors.append('Registro OPEN: identificadores duplicados')

if errors:
    for error in errors:
        print('ERRO:', error)
    sys.exit(1)
print(f'OK: {len(files)} documentos, links internos e referências RF/RNF/RB/UC/DA/ADR/SPEC/OPEN válidos.')
print('Estrutura SDD: 14 seções, cobertura de critérios/invariantes por testes derivados e ordem de dependências verificadas.')
print('Integridade documental apenas; conteúdo semântico e aprovação exigem revisão humana. Este verificador não executa testes de aplicação, segurança ou desempenho; consulte os registros de execução separados.')
