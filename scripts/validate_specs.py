
"""
Validate that implementation matches specifications.
"""
import sys
from pathlib import Path

def check_spec_files():
    """Ensure all required spec files exist"""
    required = [
        "specs/_meta.md",
        "specs/functional.md", 
        "specs/technical.md",
        "specs/openclaw_integration.md"
    ]
    
    missing = []
    for spec in required:
        if not Path(spec).exists():
            missing.append(spec)
    
    if missing:
        print(f"[FAIL] Missing spec files: {missing}")
        return False

    print("[OK] All spec files present")
    return True

def check_skill_readmes():
    """Check skill READMEs exist"""
    skill_dirs = list(Path("skills").glob("skill_*/"))
    
    if len(skill_dirs) < 3:
        print(f"[FAIL] Need at least 3 skills, found {len(skill_dirs)}")
        return False
    
    for skill_dir in skill_dirs:
        readme = skill_dir / "README.md"
        if not readme.exists():
            print(f"[FAIL] Missing README.md in {skill_dir}")
            return False

    print(f"[OK] All {len(skill_dirs)} skills have READMEs")
    return True

if __name__ == "__main__":
    spec_ok = check_spec_files()
    skills_ok = check_skill_readmes()
    
    if spec_ok and skills_ok:
        print("\n[OK] All spec validation passed")
        sys.exit(0)
    else:
        print("\n[FAIL] Spec validation failed")
        sys.exit(1)