import ast
import sys
import os
import json

def get_decorator_names(node):
    """FastAPI 라우터 데코레이터 등을 추출 (@router.get 등)"""
    decorators = []
    for dec in node.decorator_list:
        if isinstance(dec, ast.Call):
            if isinstance(dec.func, ast.Attribute):
                decorators.append(f"@{dec.func.value.id}.{dec.func.attr}(...)")
            elif isinstance(dec.func, ast.Name):
                decorators.append(f"@{dec.func.id}(...)")
        elif isinstance(dec, ast.Attribute):
            decorators.append(f"@{dec.value.id}.{dec.attr}")
        elif isinstance(dec, ast.Name):
            decorators.append(f"@{dec.id}")
    return decorators

def extract_python_skeleton(filepath, line_threshold=150):
    """파일 라인 수가 임계치를 넘으면 뼈대만, 아니면 전체 내용을 반환"""
    if not os.path.exists(filepath):
        return f"Error: File not found - {filepath}"

    with open(filepath, 'r', encoding='utf-8') as f:
        source_code = f.read()

    lines = source_code.splitlines()
    if len(lines) <= line_threshold:
        return source_code  # 파일이 작으면 그대로 반환

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return f"Syntax Error in {filepath}: {e}"

    skeleton = [f"# --- AST 구조 요약 (총 {len(lines)}라인 중 뼈대만 추출됨) ---", f"# 파일 경로: {filepath}\n"]

    for node in tree.body:
        # 클래스 구조 추출
        if isinstance(node, ast.ClassDef):
            skeleton.append(f"class {node.name}:")
            for sub_node in node.body:
                if isinstance(sub_node, ast.FunctionDef):
                    skeleton.append(f"    def {sub_node.name}(...): ...")
                elif isinstance(sub_node, ast.AsyncFunctionDef):
                    skeleton.append(f"    async def {sub_node.name}(...): ...")
            skeleton.append("")

        # 독립된 일반 함수 / 비동기 함수 (FastAPI 엔드포인트 포함) 추출
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            decorators = get_decorator_names(node)
            for dec in decorators:
                skeleton.append(dec)
            
            prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
            skeleton.append(f"{prefix} {node.name}(...): ...\n")

    skeleton.append("# ---------------------------------------------------")
    skeleton.append("# 세부 구현 내용이 필요하다면 특정 함수명이나 라인 번호를 지정하여 다시 검색하세요.")
    
    return "\n".join(skeleton)

if __name__ == "__main__":
    # 코덱스 훅(Hook)에서 전달되는 도구 인자(Tool arguments) 파싱
    # (실제 환경의 stdin 또는 환경변수 전달 방식에 맞게 조정)
    try:
        input_data = sys.stdin.read()
        if input_data:
            request = json.loads(input_data)
            # 파일 읽기 도구 호출 시 타겟 경로 추출
            target_file = request.get("command", "") or request.get("filepath", "")
            
            if target_file.endswith(".py"):
                result = extract_python_skeleton(target_file)
                print(json.dumps({"status": "success", "output": result}))
            else:
                # 파이썬 파일이 아니면 패스 (기본 동작 수행)
                print(json.dumps({"status": "pass"}))
        else:
            # 커맨드라인 직접 실행 테스트용
            if len(sys.argv) > 1:
                print(extract_python_skeleton(sys.argv[1]))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))