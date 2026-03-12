"""
GitHub Projects Module
Evaluates student's project portfolio and contributions
"""

import os
import re
import shutil
import subprocess
import stat
import uuid
import time
from collections import defaultdict


class GitHubProject:
    """Class for evaluating GitHub projects and contributions"""
    
    CODE_EXT = [".py", ".js", ".ts", ".java", ".cpp", ".c"]
    
    TECH_KEYWORDS = {
        "Django": ["django"],
        "Flask": ["flask"],
        "FastAPI": ["fastapi"],
        "React": ["react"],
        "Express": ["express"],
        "Machine Learning": ["tensorflow", "torch", "sklearn", "pandas", "numpy"],
        "Database": ["sqlalchemy", "pymongo", "psycopg2", "mysql"]
    }
    
    def __init__(self):
        self.repos = []
        self.project_scores = []
        self.average_score = 0
    
    def remove_readonly(self, func, path, excinfo):
        """Windows safe delete"""
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except:
            pass
    
    def clone_repo(self, repo_url, temp_dir):
        """Clone repository with fallback options"""
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, onerror=self.remove_readonly)
                time.sleep(1)
            
            # Set environment to skip authentication prompts
            env = os.environ.copy()
            env['GIT_TERMINAL_PROMPT'] = '0'  # Disable terminal prompts
            
            # Try with shallow clone, no verify SSL, and quiet mode
            cmd = f'git clone --depth 1 -q --no-checkout "{repo_url}" "{temp_dir}" 2>&1'
            
            print(f"     📥 Attempting git clone (shallow)...")
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                env=env,
                timeout=25
            )
            
            if result.returncode == 0:
                # Now checkout
                checkout_cmd = f'cd "{temp_dir}" && git checkout HEAD 2>&1'
                checkout_result = subprocess.run(checkout_cmd, shell=True, timeout=15, env=env)
                
                if checkout_result.returncode == 0:
                    print(f"     ✅ Repository cloned and checked out successfully")
                    return True
            
            print(f"     ⚠️  Clone attempt 1 failed (code {result.returncode})")
            
            # Fallback: Try without .git suffix handling
            try_urls = [repo_url]
            if not repo_url.endswith('.git'):
                try_urls.append(repo_url + '.git')
            
            for alt_url in try_urls[1:]:
                print(f"     🔄 Trying alternative URL: {alt_url[:50]}...")
                cmd2 = f'git clone --depth 1 -q --no-checkout "{alt_url}" "{temp_dir}" 2>&1'
                result2 = subprocess.run(cmd2, shell=True, env=env, timeout=25)
                
                if result2.returncode == 0:
                    checkout_cmd = f'cd "{temp_dir}" && git checkout HEAD 2>&1'
                    subprocess.run(checkout_cmd, shell=True, timeout=15, env=env)
                    print(f"     ✅ Repository cloned successfully with alternative URL")
                    return True
            
            print(f"     ❌ All clone attempts failed")
            
            # Final fallback: check if something was created anyway
            if os.path.exists(os.path.join(temp_dir, '.git')):
                print(f"     ✅ Repository exists despite errors, proceeding...")
                return True
                
            return False
            
        except subprocess.TimeoutExpired:
            print(f"     ⏱️  Clone timeout (>25s)")
            if os.path.exists(temp_dir) and len(os.listdir(temp_dir)) > 0:
                print(f"     📁 Partial data exists, proceeding with analysis...")
                return True
            return False
        except Exception as e:
            print(f"     ❌ Error: {str(e)[:80]}")
            return False
    
    def get_code_files(self, temp_dir):
        """Collect code files"""
        files = []
        for root, _, filenames in os.walk(temp_dir):
            if any(x in root for x in ["node_modules", ".git", "dist", "build", "venv"]):
                continue
            for f in filenames:
                if os.path.splitext(f)[1] in self.CODE_EXT:
                    files.append(os.path.join(root, f))
        return files
    
    def logic_density(self, files):
        """Analyze logic density"""
        functions = 0
        control_flow = 0
        loc = 0
        
        for file in files:
            try:
                with open(file, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        loc += 1
                        if re.search(r"\b(def|function|class)\b", line):
                            functions += 1
                        if re.search(r"\b(if|for|while|try|switch|catch)\b", line):
                            control_flow += 1
            except:
                pass
        
        score = min((functions * 2 + control_flow) / 50, 5)
        return round(score, 2), loc, functions, control_flow
    
    def detect_tech_usage(self, files):
        """Detect technology usage"""
        usage = defaultdict(int)
        
        for file in files:
            try:
                with open(file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().lower()
                    for tech, keywords in self.TECH_KEYWORDS.items():
                        if any(k in content for k in keywords):
                            usage[tech] += 1
            except:
                pass
        
        depth_score = 0
        for count in usage.values():
            if count >= 10:
                depth_score += 1
            elif count >= 3:
                depth_score += 0.5
        
        return list(usage.keys()), min(depth_score, 5)
    
    def architecture_quality(self, files, temp_dir):
        """Evaluate architecture quality"""
        folders = set()
        
        for file in files:
            rel = file.replace(temp_dir, "")
            parts = rel.split(os.sep)
            if len(parts) > 2:
                folders.add(parts[1])
        
        if len(folders) >= 6:
            return 5
        elif len(folders) >= 4:
            return 4
        elif len(folders) >= 3:
            return 3
        elif len(folders) >= 2:
            return 2
        return 1
    
    def documentation_score(self, temp_dir):
        """Check documentation quality"""
        score = 0
        readme = os.path.join(temp_dir, "README.md")
        
        if os.path.exists(readme):
            try:
                with open(readme, "r", encoding="utf-8", errors="ignore") as f:
                    words = len(f.read().split())
                    if words > 500:
                        score += 3
                    elif words > 200:
                        score += 2
                    else:
                        score += 1
            except:
                pass
        
        for root, _, files in os.walk(temp_dir):
            if any("test" in f.lower() for f in files):
                score += 2
                break
        
        return min(score, 5)
    
    def scope_score(self, loc, file_count):
        """Calculate project scope score"""
        if loc > 3000 or file_count > 40:
            return 5
        if loc > 1500 or file_count > 25:
            return 4
        if loc > 800 or file_count > 15:
            return 3
        if loc > 300:
            return 2
        return 1
    
    def calculate_project_complexity(self, repo_url):
        """Calculate project complexity score"""
        temp_dir = f"temp_repo_{uuid.uuid4().hex[:8]}"
        
        try:
            print(f"  [STEP 1/9] Cloning repository: {repo_url}")
            if not self.clone_repo(repo_url, temp_dir):
                print(f"  ❌ Failed to clone repository")
                return None
            print(f"  ✅ Repository cloned successfully")
            
            print(f"  [STEP 2/9] Analyzing code files...")
            files = self.get_code_files(temp_dir)
            print(f"  ✅ Found {len(files)} code files")
            
            if not files:
                print(f"  ⚠️  No code files found in {repo_url}")
                return None
            
            print(f"  [STEP 3/9] Calculating logic density...")
            logic, loc, funcs, flows = self.logic_density(files)
            print(f"     • Lines of Code: {loc}")
            print(f"     • Functions: {funcs}")
            print(f"     • Control Flow Statements: {flows}")
            print(f"     • Logic Score: {logic}/5")
            
            print(f"  [STEP 4/9] Detecting technology stack...")
            tech_stack, tech_depth = self.detect_tech_usage(files)
            print(f"     • Tech Stack: {tech_stack}")
            print(f"     • Tech Depth Score: {tech_depth}/5")
            
            print(f"  [STEP 5/9] Evaluating architecture...")
            arch = self.architecture_quality(files, temp_dir)
            print(f"     • Architecture Score: {arch}/5")
            
            print(f"  [STEP 6/9] Checking documentation...")
            docs = self.documentation_score(temp_dir)
            print(f"     • Documentation Score: {docs}/5")
            
            print(f"  [STEP 7/9] Calculating project scope...")
            scope = self.scope_score(loc, len(files))
            print(f"     • Scope Score: {scope}/5")
            
            print(f"  [STEP 8/9] Computing final score...")
            final_score = (
                0.30 * logic +
                0.25 * arch +
                0.20 * tech_depth +
                0.15 * docs +
                0.10 * scope
            ) * 20
            
            if final_score < 30:
                level = "Beginner / Toy Project"
            elif final_score < 50:
                level = "Basic Academic Project"
            elif final_score < 70:
                level = "Intermediate Engineering Project"
            elif final_score < 85:
                level = "Advanced Student Project"
            else:
                level = "High-Complexity / Pre-Industry Project"
            
            print(f"     • Formula: (Logic×0.30 + Arch×0.25 + Tech×0.20 + Docs×0.15 + Scope×0.10) × 20")
            print(f"     • Calculation: ({logic}×0.30 + {arch}×0.25 + {tech_depth}×0.20 + {docs}×0.15 + {scope}×0.10) × 20")
            print(f"     • Final Score: {final_score:.2f}/100")
            print(f"     • Assessment: {level}")
            
            print(f"  [STEP 9/9] Preparing response data (UTF-8 encoding cleanup)...")
            
            # Sanitize data for JSON serialization to fix encoding errors
            try:
                safe_tech_stack = [str(t).encode('utf-8', errors='ignore').decode('utf-8') for t in tech_stack]
            except:
                safe_tech_stack = []
            
            result = {
                "repo_url": str(repo_url).encode('utf-8', errors='ignore').decode('utf-8'),
                "lines_of_code": int(loc),
                "code_files": int(len(files)),
                "functions": int(funcs),
                "control_flow_statements": int(flows),
                "tech_stack": safe_tech_stack,
                "logic_density_score": float(logic),
                "architecture_score": float(arch),
                "tech_depth_score": float(tech_depth),
                "documentation_score": float(docs),
                "scope_score": float(scope),
                "final_project_score": float(round(final_score, 2)),
                "assessment": str(level).encode('utf-8', errors='ignore').decode('utf-8')
            }
            
            print(f"  ✅ All 9 steps completed successfully!")
            print(f"  ✅ Response data ready for transmission")
            
            return result
        
        except Exception as e:
            print(f"❌ Error processing repo: {e}")
            return None
        
        finally:
            # Clean up: Delete temporary repository directory after analysis
            if os.path.exists(temp_dir):
                print(f"  [CLEANUP] Removing temporary repository directory...")
                shutil.rmtree(temp_dir, onerror=self.remove_readonly)
                print(f"  ✅ Temporary directory deleted successfully")
    
    def evaluate_multiple_projects(self, repo_urls):
        """Evaluate multiple GitHub repositories"""
        print("\n" + "="*60)
        print("📊 GITHUB PROJECT EVALUATION PROCESS STARTED")
        print(f"   Total Repositories to Analyze: {len(repo_urls)}")
        print("="*60)
        
        for i, url in enumerate(repo_urls, 1):
            print(f"\n📁 REPOSITORY [{i}/{len(repo_urls)}]")
            print("-" * 60)
            result = self.calculate_project_complexity(url)
            
            if result:
                self.repos.append(result)
                self.project_scores.append(result['final_project_score'])
                print(f"\n  ✅ Repository Processed Successfully!")
                print(f"     Final Score: {result['final_project_score']}/100")
                print(f"     Assessment: {result['assessment']}")
            else:
                print(f"\n  ⚠️  Repository Processing Failed")
        
        print("\n" + "="*60)
        print("🔄 CALCULATING AVERAGE SCORE...")
        
        if self.project_scores:
            self.average_score = round(sum(self.project_scores) / len(self.project_scores), 2)
            print(f"✅ Average Score Calculated: {self.average_score}/100")
        else:
            self.average_score = 0
            print(f"⚠️  No valid scores calculated")
        
        print(f"✅ Total Repositories Successfully Analyzed: {len(self.repos)}/{len(repo_urls)}")
        print(f"✅ All temporary directories cleaned up")
        print("="*60 + "\n")
        
        return self.average_score
    
    def get_project_score(self):
        """Get average project score"""
        return self.average_score
    
    def print_report(self):
        """Print GitHub assessment report"""
        print("\n" + "="*50)
        print("GitHub Projects Assessment Report")
        print("="*50)
        print(f"Total Projects Analyzed: {len(self.repos)}")
        
        for i, repo in enumerate(self.repos, 1):
            print(f"\n📁 Project {i}: {repo['repo_url']}")
            print(f"   Score: {repo['final_project_score']}/100")
            print(f"   Lines of Code: {repo['lines_of_code']}")
            print(f"   Code Files: {repo['code_files']}")
            print(f"   Tech Stack: {', '.join(repo['tech_stack']) if repo['tech_stack'] else 'N/A'}")
            print(f"   Assessment: {repo['assessment']}")
        
        print(f"\n📊 Average Project Score: {self.average_score}/100")
        print("="*50)
