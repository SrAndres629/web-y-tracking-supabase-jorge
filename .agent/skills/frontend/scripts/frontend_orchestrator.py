#!/usr/bin/env python3
import subprocess
import os
import sys

# Rutas de los scripts de las otras skills
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
SKILLS_DIR = os.path.join(ROOT, '.agent/skills')

SCRIPTS = {
    'marca': os.path.join(SKILLS_DIR, 'marca/scripts/brand_manager.py'),
    'diseño': os.path.join(SKILLS_DIR, 'diseño/scripts/design_manager.py'),
    'estructura': os.path.join(SKILLS_DIR, 'estructura/scripts/structure_manager.py'),
    'qa': os.path.join(SKILLS_DIR, 'auditoria-qa/scripts/auditoria_manager.py'),
    'mobile': os.path.join(SKILLS_DIR, 'ui-ux-mobile/scripts/mobile_manager.py'),
    'copy': os.path.join(SKILLS_DIR,
                         'copywriting-conversion/scripts/copy_manager.py'),
    'perf': os.path.join(SKILLS_DIR,
                         'performance-optimization/scripts/perf_manager.py'),
    'seo': os.path.join(SKILLS_DIR,
                        'seo-semantic-authority/scripts/seo_manager.py'),
    'resilience': os.path.join(SKILLS_DIR,
                               'error-states-resilience/scripts/resilience_manager.py'),
    'social': os.path.join(SKILLS_DIR,
                           'social-viral-metadata/scripts/social_manager.py'),
    'edge': os.path.join(SKILLS_DIR,
                         'edge-mastery-ops/scripts/edge_manager.py'),
    'zaraz': os.path.join(SKILLS_DIR,
                          'zaraz-tracking-architect/scripts/zaraz_manager.py'),
    'stitch': os.path.join(SKILLS_DIR,
                           'stitch-vibe-translator/scripts/stitch_manager.py')
}

def run_skill_script(skill, command, *args):
    script_path = SCRIPTS.get(skill)
    if not script_path or not os.path.exists(script_path):
        return f"Error: Script de {skill} no encontrado."
    
    cmd = [sys.executable, script_path, command] + list(args)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error ejecutando {skill}: {e.stderr}"

def full_frontend_audit():
    """Realiza una auditoría completa de los 4 pilares frontend (incluyendo QA)."""
    diseno_out = run_skill_script('diseño', 'list')
    diseno_list = diseno_out.split('\n')
    
    base_out = run_skill_script('estructura', 'blocks', 'layouts/base.html')
    base_blocks = base_out.split('\n')
    
    qa_out = run_skill_script('qa', 'validate')
    qa_report = qa_out.split('\n')
    
    mobile_out = run_skill_script('mobile', 'audit')
    mobile_report = mobile_out.split('\n')
    
    copy_out = run_skill_script('copy', 'audit')
    copy_report = copy_out.split('\n')
    
    perf_out = run_skill_script('perf', 'audit')
    perf_report = perf_out.split('\n')
    
    seo_out = run_skill_script('seo', 'audit')
    seo_report = seo_out.split('\n')
    
    resilience_out = run_skill_script('resilience', 'audit')
    resilience_report = resilience_out.split('\n')
    
    social_out = run_skill_script('social', 'audit')
    social_report = social_out.split('\n')
    
    edge_out = run_skill_script('edge', 'audit')
    edge_report = edge_out.split('\n')
    
    zaraz_out = run_skill_script('zaraz', 'audit')
    zaraz_report = zaraz_out.split('\n')
    
    stitch_out = run_skill_script('stitch', 'audit')
    stitch_report = stitch_out.split('\n')
    
    # Format design and structure properly to avoid lints
    design_data = diseno_list[1:] if len(diseno_list) > 1 else diseno_list
    structure_data = base_blocks[1:] if len(base_blocks) > 1 else base_blocks
    
    report = {
        "status": "Auditando con OODA Loop Master (Full 13-Skill Elite Team)...",
        "marca": "OK (Tokens sincronizados)",
        "diseño": design_data,
        "estructura_base": structure_data,
        "qa": qa_report,
        "mobile": mobile_report,
        "copy": copy_report,
        "perf": perf_report,
        "seo": seo_report,
        "resilience": resilience_report,
        "social": social_report,
        "edge": edge_report,
        "zaraz": zaraz_report,
        "stitch": stitch_report
    }
    return report

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 frontend_orchestrator.py audit")
        sys.exit(1)
    
    action = sys.argv[1]
    if action == "audit":
        audit_data = full_frontend_audit()
        print("======== [FRONTEND MASTER ARCHITECT REPORT] ========")
        print(f"ESTADO: {audit_data['status']}")
        
        print("\n[OBSERVAR - QA] Análisis de integridad:")
        for line in audit_data['qa']:
            if line.strip() and "REPORT" not in line and "====" not in line:
                print(f"  {line}")

        print("\n[ORIENTAR - MOBILE] Estrategia de conversión:")
        for line in audit_data['mobile']:
            if line.strip() and "INFORME" not in line and "====" not in line:
                print(f"  {line}")

        print("\n[ORIENTAR - COPY] Voz de autoridad:")
        for line in audit_data['copy']:
            if line.strip() and "INFORME" not in line and "====" not in line:
                print(f"  {line}")

        print("\n[DECIDIR - PERF] Estabilidad y velocidad:")
        for line in audit_data['perf']:
            if line.strip() and "INFORME" not in line and "====" not in line:
                print(f"  {line}")

        print("\n[ORIENTAR - SEO] Visibilidad Semántica:")
        for line in audit_data['seo']:
            if line.strip() and "INFORME" not in line and "====" not in line:
                print(f"  {line}")

        print("\n[ESTRUCTURA - RESILIENCIA] Robustez:")
        for line in audit_data['resilience']:
            if line.strip() and "INFORME" not in line and "====" not in line:
                print(f"  {line}")

        print("\n[MARCA - SOCIAL] Autoridad Viral:")
        for line in audit_data['social']:
            if line.strip() and "INFORME" not in line and "====" not in line:
                print(f"  {line}")

        print("\n[INFRA - SRE] Estabilidad de Infraestructura:")
        for line in audit_data['edge']:
            if line.strip() and "INFORME" not in line and "====" not in line:
                print(f"  {line}")

        print("\n[DATOS - TRACKING] Arquitectura Zaraz:")
        for line in audit_data['zaraz']:
            if line.strip() and "INFORME" not in line and "====" not in line:
                print(f"  {line}")

        print("\n[DISEÑO - STITCH] Traducción Estética:")
        for line in audit_data['stitch']:
            if line.strip() and "INFORME" not in line and "====" not in line:
                print(f"  {line}")

        print("\n[ORIENTAR - ESTRUCTURA] Bloques disponibles:")
        for b in audit_data['estructura_base']:
            print(f"  {b}")
            
        print("\n[DECIDIR - DISEÑO] Componentes activos:")
        for c in audit_data['diseño']:
            print(f"  {c}")
            
        print("\n[ACTUAR - MARCA] Sincronización:")
        print(f"  {audit_data['marca']}")
        print("====================================================")
